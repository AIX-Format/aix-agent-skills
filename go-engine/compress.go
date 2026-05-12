package main

import (
	"math"
)

// CompressionResult is the unified return value for all compressors.
// Callers can read CompressionRatio for analytics regardless of which
// algorithm produced the result.
//
// CompressionRatio reflects the *storage* size reduction. The baseline
// implementations in this file emit []int8 (1 byte per element) regardless
// of the logical bit width, so TurboQuant always reports 8.0 (64-bit
// float -> 8-bit int) even when called with bits<8. A bit-packing variant
// could legitimately report a higher ratio.
type CompressionResult struct {
	Method           string      `json:"method"`
	Data             interface{} `json:"data"`
	OriginalDim      int         `json:"original_dim"`
	CompressedDim    int         `json:"compressed_dim"`
	Bits             int         `json:"bits,omitempty"`
	Scale            float64     `json:"scale,omitempty"`
	CompressionRatio float64     `json:"compression_ratio"`
}

// sanitizeEmbedding replaces any NaN/Inf values with 0 so downstream
// quantization is deterministic. Returns the (possibly new) slice and the
// observed max absolute value.
func sanitizeEmbedding(embedding []float64) ([]float64, float64) {
	maxAbs := 0.0
	for i, v := range embedding {
		if math.IsNaN(v) || math.IsInf(v, 0) {
			embedding[i] = 0
			continue
		}
		if a := math.Abs(v); a > maxAbs {
			maxAbs = a
		}
	}
	return embedding, maxAbs
}

// TurboQuantCompress quantizes a float64 vector to N-bit signed integers.
// Symmetric quantization: each value normalized to [-maxAbs, maxAbs] then
// scaled into the int range allowed by `bits`. Returns the packed []int8
// representation along with the scale factor used.
//
// NaN and Inf inputs are coerced to 0 to keep the output deterministic;
// without this, math.Round(NaN/scale) is NaN and the int8 conversion is
// architecture-dependent.
//
// CompressionRatio is fixed at 8.0 because the output is []int8 (1 byte
// per element) regardless of the requested logical bit width. A true
// bit-packed variant would report 64.0/bits.
func TurboQuantCompress(embedding []float64, bits int) CompressionResult {
	if bits <= 0 || bits > 8 {
		bits = 8
	}
	originalDim := len(embedding)
	if originalDim == 0 {
		return CompressionResult{
			Method:           "turbo_quant",
			Data:             []int8{},
			OriginalDim:      0,
			CompressedDim:    0,
			Bits:             bits,
			Scale:            0,
			CompressionRatio: 0,
		}
	}

	// Mutate-in-place is intentional: callers passing transient embeddings
	// do not need a copy, and avoiding the allocation matters for the hot
	// path. If a caller needs the input preserved, copy before calling.
	embedding, maxAbs := sanitizeEmbedding(embedding)
	if maxAbs == 0 {
		return CompressionResult{
			Method:           "turbo_quant",
			Data:             make([]int8, originalDim),
			OriginalDim:      originalDim,
			CompressedDim:    originalDim,
			Bits:             bits,
			Scale:            0,
			CompressionRatio: 8.0,
		}
	}

	levels := float64(int(1) << (bits - 1)) // e.g. bits=8 -> 128
	scale := maxAbs / levels
	out := make([]int8, originalDim)
	for i, v := range embedding {
		q := math.Round(v / scale)
		if q > levels-1 {
			q = levels - 1
		} else if q < -levels {
			q = -levels
		}
		out[i] = int8(q)
	}
	return CompressionResult{
		Method:           "turbo_quant",
		Data:             out,
		OriginalDim:      originalDim,
		CompressedDim:    originalDim,
		Bits:             bits,
		Scale:            scale,
		CompressionRatio: 8.0, // []int8 = 1 byte; 64-bit float -> 1 byte = 8x
	}
}

// QJLCompress is a Johnson-Lindenstrauss style random projection compressor.
// Baseline implementation: project the embedding onto a deterministic
// pseudo-random basis of size len(embedding)/2. Returns the projected vector.
//
// Preserves approximate pairwise distances and is sufficient for resonance
// comparisons. The sign of each contribution is derived from the least
// significant bit of an integer mix; the bitwise check is robust against
// negative remainders that `% 2` can produce in Go when intermediate
// values overflow into negative ints.
func QJLCompress(embedding []float64) CompressionResult {
	srcDim := len(embedding)
	if srcDim == 0 {
		return CompressionResult{
			Method:           "qjl",
			Data:             []float64{},
			OriginalDim:      0,
			CompressedDim:    0,
			CompressionRatio: 0,
		}
	}
	dstDim := srcDim / 2
	if dstDim < 1 {
		dstDim = 1
	}
	out := make([]float64, dstDim)
	scale := 1.0 / math.Sqrt(float64(srcDim))
	for i := 0; i < dstDim; i++ {
		var acc float64
		for j := 0; j < srcDim; j++ {
			sign := 1.0
			// Bitwise LSB check avoids the sign-of-modulo trap that
			// occurs in Go when intermediate ints overflow negative.
			if ((i*31+j)*17)&1 != 0 {
				sign = -1.0
			}
			acc += sign * embedding[j]
		}
		out[i] = acc * scale
	}
	return CompressionResult{
		Method:           "qjl",
		Data:             out,
		OriginalDim:      srcDim,
		CompressedDim:    dstDim,
		CompressionRatio: float64(srcDim) / float64(dstDim),
	}
}

// PolarQuantCompress encodes the embedding as polar (r, theta) pairs.
// For an even-dimensional D, returns D/2 pairs. For an odd-dimensional D,
// the trailing element is preserved as a (|v|, 0) pair so no input data is
// silently dropped. Output is flat [r0, theta0, r1, theta1, ...]; the
// representation is more interpretable but not smaller in size, so the
// compression ratio is 1.0.
func PolarQuantCompress(embedding []float64) CompressionResult {
	srcDim := len(embedding)
	if srcDim == 0 {
		return CompressionResult{
			Method:           "polar",
			Data:             []float64{},
			OriginalDim:      0,
			CompressedDim:    0,
			CompressionRatio: 0,
		}
	}
	pairs := srcDim / 2
	hasTrailing := srcDim%2 == 1

	outLen := 2 * pairs
	if hasTrailing {
		outLen += 2
	}
	if outLen == 0 {
		// srcDim was effectively 0; handled above, but defensive.
		return CompressionResult{
			Method:           "polar",
			Data:             []float64{},
			OriginalDim:      srcDim,
			CompressedDim:    0,
			CompressionRatio: 0,
		}
	}

	out := make([]float64, outLen)
	for k := 0; k < pairs; k++ {
		x := embedding[2*k]
		y := embedding[2*k+1]
		out[2*k] = math.Sqrt(x*x + y*y)
		out[2*k+1] = math.Atan2(y, x)
	}
	if hasTrailing {
		// Preserve the trailing scalar as (|v|, 0): magnitude with zero phase.
		out[2*pairs] = math.Abs(embedding[srcDim-1])
		out[2*pairs+1] = 0.0
	}
	return CompressionResult{
		Method:           "polar",
		Data:             out,
		OriginalDim:      srcDim,
		CompressedDim:    outLen,
		CompressionRatio: 1.0,
	}
}
