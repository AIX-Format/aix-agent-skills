package main

import (
	"math"
	"testing"
)

func TestEuclideanDistance(t *testing.T) {
	tests := []struct {
		name     string
		a        []float64
		b        []float64
		expected float64
	}{
		{"Same length", []float64{0, 0}, []float64{3, 4}, 5.0},
		{"Different length", []float64{0, 0}, []float64{3}, math.MaxFloat64},
		{"Zero length", []float64{}, []float64{}, 0.0},
		{"3D space", []float64{1, 2, 3}, []float64{4, 5, 6}, math.Sqrt(27)},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := euclideanDistance(tt.a, tt.b)
			if math.Abs(got-tt.expected) > 1e-9 {
				t.Errorf("%s: euclideanDistance(%v, %v) = %v; want %v", tt.name, tt.a, tt.b, got, tt.expected)
			}
		})
	}
}

func TestVariance(t *testing.T) {
	tests := []struct {
		name     string
		data     []float64
		expected float64
	}{
		{"Empty slice", []float64{}, 0.0},
		{"Single element", []float64{10.0}, 0.0},
		{"Multiple elements", []float64{2, 4, 4, 4, 5, 5, 7, 9}, 4.0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := variance(tt.data)
			if math.Abs(got-tt.expected) > 1e-9 {
				t.Errorf("%s: variance(%v) = %v; want %v", tt.name, tt.data, got, tt.expected)
			}
		})
	}
}

func TestCalculateLIDMLE(t *testing.T) {
	tests := []struct {
		name      string
		distances []float64
		expected  float64
	}{
		{"Less than 2 distances", []float64{1.0}, 1.0},
		{"Furthest distance is 0", []float64{0.0, 0.0}, 1.0},
		{"Normal case", []float64{1.0, 2.0, 3.0}, 1.3297188058850222}, // -2 / (log(1/3) + log(2/3))
		{"All same distances", []float64{2.0, 2.0, 2.0}, 1.0},       // sumLog will be 0
		{"Smallest possible LID", []float64{0.001, 100.0}, 1.0},     // MLE would be ~0.086, but capped at 1.0
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := calculateLIDMLE(tt.distances)
			if math.Abs(got-tt.expected) > 1e-7 {
				t.Errorf("%s: calculateLIDMLE(%v) = %v; want %v", tt.name, tt.distances, got, tt.expected)
			}
		})
	}
}

func TestCalculateLID(t *testing.T) {
	embedding := []float64{0, 0}
	refs := [][]float64{
		{1, 1},
		{2, 2},
		{3, 3},
		{4, 4},
		{5, 5},
	}

	t.Run("Standard input", func(t *testing.T) {
		res := CalculateLID(embedding, refs, 3)
		if len(res.NearestNeighbors) != 3 {
			t.Errorf("expected 3 nearest neighbors, got %d", len(res.NearestNeighbors))
		}
		if res.LID < 1.0 {
			t.Errorf("LID should be at least 1.0, got %f", res.LID)
		}
	})

	t.Run("IsHighResonance constraint", func(t *testing.T) {
		// Current implementation caps LID at 1.0, which means Resonance <= 0.5.
		// Threshold is 0.7, so IsHighResonance will be false.
		res := CalculateLID(embedding, refs, 3)
		if res.IsHighResonance {
			t.Errorf("IsHighResonance should be false given current LID cap of 1.0")
		}
	})

	t.Run("k <= 0", func(t *testing.T) {
		// Should default to 7, but we only have 5 refs, so it should be 5
		res := CalculateLID(embedding, refs, 0)
		if len(res.NearestNeighbors) != 5 {
			t.Errorf("expected 5 nearest neighbors when k=0 and len(refs)=5, got %d", len(res.NearestNeighbors))
		}
	})

	t.Run("k > references", func(t *testing.T) {
		res := CalculateLID(embedding, refs, 10)
		if len(res.NearestNeighbors) != 5 {
			t.Errorf("expected 5 nearest neighbors when k=10 and len(refs)=5, got %d", len(res.NearestNeighbors))
		}
	})
}

func TestMin(t *testing.T) {
	if min(1, 2) != 1 {
		t.Errorf("min(1, 2) = %d; want 1", min(1, 2))
	}
	if min(5, 3) != 3 {
		t.Errorf("min(5, 3) = %d; want 3", min(5, 3))
	}
}

func TestEuclideanDistance_Extended(t *testing.T) {
	tests := []struct {
		name     string
		a        []float64
		b        []float64
		expected float64
	}{
		// Negative coordinates: distance should be the same as positive mirror
		{"Negative coordinates", []float64{-3, -4}, []float64{0, 0}, 5.0},
		// 1D vectors
		{"1D same point", []float64{7.0}, []float64{7.0}, 0.0},
		{"1D distance", []float64{0.0}, []float64{5.0}, 5.0},
		// One nil / empty vs non-empty → different lengths → MaxFloat64
		{"One empty one non-empty", []float64{}, []float64{1.0}, math.MaxFloat64},
		// Symmetry: distance(a,b) == distance(b,a)
		{"Symmetry check a", []float64{1, 2}, []float64{4, 6}, 5.0},
		{"Symmetry check b", []float64{4, 6}, []float64{1, 2}, 5.0},
		// High-dimensional identical vectors
		{"High-dim identical", []float64{1, 2, 3, 4, 5}, []float64{1, 2, 3, 4, 5}, 0.0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := euclideanDistance(tt.a, tt.b)
			if math.Abs(got-tt.expected) > 1e-9 {
				t.Errorf("euclideanDistance(%v, %v) = %v; want %v", tt.a, tt.b, got, tt.expected)
			}
		})
	}
}

func TestVariance_Extended(t *testing.T) {
	tests := []struct {
		name     string
		data     []float64
		expected float64
	}{
		// Two elements: var([a,b]) = ((a-m)^2 + (b-m)^2) / 2 where m=(a+b)/2
		{"Two elements", []float64{0.0, 4.0}, 4.0},
		// All zeros: variance must be 0
		{"All zeros", []float64{0.0, 0.0, 0.0}, 0.0},
		// Negative values: variance is always non-negative
		{"Negative values", []float64{-2.0, -2.0, -2.0}, 0.0},
		// Mixed positive and negative
		{"Mixed positive negative", []float64{-1.0, 1.0}, 1.0},
		// Large uniform spread: var([0, 10]) = ((0-5)^2 + (10-5)^2) / 2 = 25
		{"Large uniform spread", []float64{0.0, 10.0}, 25.0},
		// Identical non-zero elements
		{"Identical non-zero", []float64{5.0, 5.0, 5.0, 5.0}, 0.0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := variance(tt.data)
			if math.Abs(got-tt.expected) > 1e-9 {
				t.Errorf("variance(%v) = %v; want %v", tt.data, got, tt.expected)
			}
		})
	}
}

func TestCalculateLIDMLE_Extended(t *testing.T) {
	tests := []struct {
		name      string
		distances []float64
		checkFn   func(got float64) bool
		wantDesc  string
	}{
		{
			// Exactly 2 distances: boundary between "< 2" guard and normal path
			// distances = [1.0, 2.0]: rk=2.0, sumLog = log(1/2) = -0.693..., lid = -1 / (-0.693) ≈ 1.443
			name:     "Exactly 2 distances",
			distances: []float64{1.0, 2.0},
			checkFn:  func(got float64) bool { return math.Abs(got-1.4426950408889634) < 1e-7 },
			wantDesc: "≈ 1.4426950408889634",
		},
		{
			// First distance is 0 but rk (furthest) is non-zero: the 0 term is skipped (log branch)
			// distances = [0.0, 3.0]: rk=3.0, distances[0]=0 → skipped, sumLog=0 → returns 1.0
			name:     "First distance zero rk nonzero",
			distances: []float64{0.0, 3.0},
			checkFn:  func(got float64) bool { return got == 1.0 },
			wantDesc: "1.0 (sumLog stays 0 because distance[0] is skipped)",
		},
		{
			// Result is always >= 1.0 (enforced by math.Max)
			name:     "Result always >= 1.0",
			distances: []float64{1.0, 2.0, 3.0, 4.0, 5.0},
			checkFn:  func(got float64) bool { return got >= 1.0 },
			wantDesc: ">= 1.0",
		},
		{
			// Empty distances slice (k=0 < 2): returns 1.0
			name:     "Empty distances",
			distances: []float64{},
			checkFn:  func(got float64) bool { return got == 1.0 },
			wantDesc: "1.0",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := calculateLIDMLE(tt.distances)
			if !tt.checkFn(got) {
				t.Errorf("calculateLIDMLE(%v) = %v; want %s", tt.distances, got, tt.wantDesc)
			}
		})
	}
}

func TestCalculateLID_Extended(t *testing.T) {
	t.Run("Empty reference embeddings", func(t *testing.T) {
		embedding := []float64{1.0, 2.0}
		res := CalculateLID(embedding, [][]float64{}, 3)
		// With no refs, distances is empty, kNearest is empty, LID defaults to 1.0
		if res.LID != 1.0 {
			t.Errorf("expected LID=1.0 for empty refs, got %f", res.LID)
		}
		if len(res.NearestNeighbors) != 0 {
			t.Errorf("expected 0 nearest neighbors for empty refs, got %d", len(res.NearestNeighbors))
		}
	})

	t.Run("Single reference embedding", func(t *testing.T) {
		embedding := []float64{0.0, 0.0}
		refs := [][]float64{{3.0, 4.0}}
		res := CalculateLID(embedding, refs, 3)
		if len(res.NearestNeighbors) != 1 {
			t.Errorf("expected 1 nearest neighbor, got %d", len(res.NearestNeighbors))
		}
		if math.Abs(res.NearestNeighbors[0]-5.0) > 1e-9 {
			t.Errorf("expected nearest neighbor distance 5.0, got %f", res.NearestNeighbors[0])
		}
	})

	t.Run("Resonance equals 1/(1+LID)", func(t *testing.T) {
		embedding := []float64{0, 0}
		refs := [][]float64{{1, 0}, {2, 0}, {3, 0}}
		res := CalculateLID(embedding, refs, 3)
		expected := 1.0 / (1.0 + res.LID)
		if math.Abs(res.Resonance-expected) > 1e-9 {
			t.Errorf("Resonance = %f; want 1/(1+%f) = %f", res.Resonance, res.LID, expected)
		}
	})

	t.Run("Complexity equals variance of kNearest", func(t *testing.T) {
		embedding := []float64{0, 0}
		refs := [][]float64{{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}}
		res := CalculateLID(embedding, refs, 3)
		expectedComplexity := variance(res.NearestNeighbors)
		if math.Abs(res.Complexity-expectedComplexity) > 1e-9 {
			t.Errorf("Complexity = %f; want variance(NearestNeighbors) = %f", res.Complexity, expectedComplexity)
		}
	})

	t.Run("NearestNeighbors are sorted ascending", func(t *testing.T) {
		embedding := []float64{0, 0}
		refs := [][]float64{{5, 0}, {1, 0}, {3, 0}, {2, 0}, {4, 0}}
		res := CalculateLID(embedding, refs, 5)
		for i := 1; i < len(res.NearestNeighbors); i++ {
			if res.NearestNeighbors[i] < res.NearestNeighbors[i-1] {
				t.Errorf("NearestNeighbors not sorted at index %d: %v", i, res.NearestNeighbors)
				break
			}
		}
	})

	t.Run("k=1 returns single neighbor", func(t *testing.T) {
		embedding := []float64{0, 0}
		refs := [][]float64{{1, 0}, {2, 0}, {3, 0}}
		res := CalculateLID(embedding, refs, 1)
		if len(res.NearestNeighbors) != 1 {
			t.Errorf("expected 1 nearest neighbor for k=1, got %d", len(res.NearestNeighbors))
		}
		// With k=1, calculateLIDMLE returns 1.0 (k < 2 guard)
		if res.LID != 1.0 {
			t.Errorf("expected LID=1.0 for k=1, got %f", res.LID)
		}
	})

	t.Run("Resonance is in (0, 1] range", func(t *testing.T) {
		embedding := []float64{1.0, 1.0}
		refs := [][]float64{{2, 2}, {3, 3}, {4, 4}, {5, 5}, {6, 6}}
		res := CalculateLID(embedding, refs, 4)
		if res.Resonance <= 0 || res.Resonance > 1.0 {
			t.Errorf("Resonance %f is outside expected range (0, 1]", res.Resonance)
		}
	})

	t.Run("LID is non-negative", func(t *testing.T) {
		embedding := []float64{0, 0}
		refs := [][]float64{{1, 1}, {2, 2}, {3, 3}}
		res := CalculateLID(embedding, refs, 3)
		if res.LID < 0 {
			t.Errorf("LID should never be negative, got %f", res.LID)
		}
	})
}

func TestMin_Extended(t *testing.T) {
	tests := []struct {
		name     string
		a, b     int
		expected int
	}{
		{"Equal values", 3, 3, 3},
		{"Zero and positive", 0, 5, 0},
		{"Positive and zero", 7, 0, 0},
		{"Negative a", -1, 1, -1},
		{"Negative b", 2, -3, -3},
		{"Both negative", -5, -2, -5},
		{"Large values", 1000000, 999999, 999999},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := min(tt.a, tt.b)
			if got != tt.expected {
				t.Errorf("min(%d, %d) = %d; want %d", tt.a, tt.b, got, tt.expected)
			}
		})
	}
}
