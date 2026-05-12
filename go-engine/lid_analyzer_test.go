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
