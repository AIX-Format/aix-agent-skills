package main

import (
	"math"
)

// CompressionResult is the unified return value for all compressors.
// Callers can read CompressionRatio for analytics regardless of which
// algorithm produced the result.
type CompressionResult struct {
	Method           string      `json:"method"`
	Data             interface{} `json:"data"`
	OriginalDim      int         `json:"original_dim"`
	CompressedDim    int         `json:"compressed_dim"`
	Bits             int         `json:"bits,omitempty"`
	Scale            float64     `json:"scale,omitempty"`
	CompressionRatio float64     `json:"compression_ratio"`
}

// TurboQuantCompress quantizes a float64 vector to N-bit signed integers.
// Symmetric quantization: each value normalized to [-maxAbs, maxAbs] then
// scaled into the int range allowed by `bits`. Returns the packed []int8
// representation along with the scale factor used.
//
// CompressionRatio = (original bytes) / (compressed bytes), where original
// is 8 bytes/element (float64) and compressed is `bits / 8` bytes/element.
//
// NOTE: This is the reference implementation. Performance-tuned variants
// TurboQuantCompress quantizes an embedding into signed 8-bit integers using symmetric per-vector scaling.
// 
// TurboQuantCompress clamps the requested `bits` to the valid range (values <= 0 or > 8 are set to 8), computes a scale from the maximum absolute component, and maps each element to the integer range [-2^(bits-1), 2^(bits-1)-1] with rounding and clamping. For an empty input it returns an empty `[]int8` payload; for an all-zero input it returns a zeroed `[]int8` of the same length with `Scale = 0`. The returned CompressionResult uses `Method = "turbo_quant"`, sets `OriginalDim` and `CompressedDim` to the input length, includes the (possibly adjusted) `Bits` and computed `Scale` when applicable, and records `CompressionRatio = 64.0 / float64(bits)`.
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

	// Find max magnitude for symmetric quantization
	maxAbs := 0.0
	for _, v := range embedding {
		if a := math.Abs(v); a > maxAbs {
			maxAbs = a
		}
	}
	if maxAbs == 0 {
		return CompressionResult{
			Method:           "turbo_quant",
			Data:             make([]int8, originalDim),
			OriginalDim:      originalDim,
			CompressedDim:    originalDim,
			Bits:             bits,
			Scale:            0,
			CompressionRatio: 64.0 / float64(bits),
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
		CompressionRatio: 64.0 / float64(bits), // float64 (8 bytes) -> bits/8 bytes
	}
}

// QJLCompress is a Johnson-Lindenstrauss style random projection compressor.
// Baseline implementation: project the embedding onto a deterministic
// pseudo-random basis of size len(embedding)/2. Returns the projected vector.
//
// Preserves approximate pairwise distances and is sufficient for resonance
// comparisons. Production implementation should use a true Gaussian random
// input length, CompressedDim set to the output length, and CompressionRatio equal to float64(original)/float64(compressed).
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
			if ((i*31+j)*17)%2 == 1 {
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
// For dimension D, returns D/2 pairs, useful when angular structure
// matters more than per-axis magnitude. Output is flat
// [r0, theta0, r1, theta1, ...]; dimensionality is preserved
// (same count of floats out as in), so compression ratio is 1.0 in size
// PolarQuantCompress converts an embedding into flat polar-coordinate pairs (r, theta)
// computed from consecutive component pairs of the input.
//
// For an empty input it returns an empty Data payload and zero dimensions.
// If the input has a single element it returns Data = {abs(x), 0.0}, CompressedDim = 2
// and CompressionRatio = 0.5. For inputs with length >= 2 it converts each pair (x,y)
// into r = sqrt(x*x + y*y) and theta = atan2(y, x), sets Method = "polar",
// CompressedDim = 2*(len(embedding)/2) and CompressionRatio = 1.0.
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
	if pairs == 0 {
		return CompressionResult{
			Method:           "polar",
			Data:             []float64{math.Abs(embedding[0]), 0.0},
			OriginalDim:      srcDim,
			CompressedDim:    2,
			CompressionRatio: 0.5,
		}
	}
	out := make([]float64, 2*pairs)
	for k := 0; k < pairs; k++ {
		x := embedding[2*k]
		y := embedding[2*k+1]
		out[2*k] = math.Sqrt(x*x + y*y)
		out[2*k+1] = math.Atan2(y, x)
	}
	return CompressionResult{
		Method:           "polar",
		Data:             out,
		OriginalDim:      srcDim,
		CompressedDim:    2 * pairs,
		CompressionRatio: 1.0,
	}
}
