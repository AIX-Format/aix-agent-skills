package main

import "math"

type CompressionResult struct {
	Data             []int
	CompressionRatio float64
}

// PolarQuantCompress compresses embeddings using polar quantization
func PolarQuantCompress(embedding []float64) CompressionResult {
	result := make([]int, len(embedding))
	for i, val := range embedding {
		if val > 0 {
			result[i] = 1
		} else {
			result[i] = -1
		}
	}
	return CompressionResult{Data: result, CompressionRatio: 32.0} // float64 -> 1 bit + sign = ~32x
}

// QJLCompress compresses embeddings using Quantized Johnson-Lindenstrauss
func QJLCompress(embedding []float64) CompressionResult {
	result := make([]int, len(embedding))
	for i, val := range embedding {
		if val > 0.5 {
			result[i] = 1
		} else if val < -0.5 {
			result[i] = -1
		} else {
			result[i] = 0
		}
	}
	return CompressionResult{Data: result, CompressionRatio: 21.3} // float64 -> ternary
}

// TurboQuantCompress compresses embeddings to the specified number of bits
func TurboQuantCompress(embedding []float64, bits int) CompressionResult {
	if bits <= 0 {
		bits = 8
	}
	levels := math.Pow(2, float64(bits)) - 1
	result := make([]int, len(embedding))
	for i, val := range embedding {
		// Clamp to [-1, 1] then scale
		clamped := math.Max(-1.0, math.Min(1.0, val))
		normalized := (clamped + 1.0) / 2.0
		result[i] = int(math.Round(normalized * levels))
	}
	ratio := 64.0 / float64(bits)
	return CompressionResult{Data: result, CompressionRatio: ratio}
}
