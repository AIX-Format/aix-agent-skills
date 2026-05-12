/**
 * Fatiha Topology Module
 * Implements topological analysis for Quranic patterns, specifically focusing on Surah Al-Fatiha.
 * Used for "Pulse 3-6-9" state checks and memory resonance analysis.
 */
export interface TopologyResult {
    h0: number;
    h1: number;
    edges: number;
}
export type CharVector = Record<string, number>;
/**
 * Generates a character frequency vector from text.
 */
export declare function getCharVector(text: string): CharVector;
/**
 * Calculates cosine similarity between two character vectors.
 */
export declare function cosineSimilarity(v1: CharVector, v2: CharVector): number;
/**
 * Calculates Shannon entropy of a text based on character frequency.
 */
export declare function calculateEntropy(text: string): number;
/**
 * Computes the topology (Betti numbers) of a set of verses based on similarity thresholds.
 */
export declare function computeTopology(verses: string[], threshold?: number): TopologyResult;
/**
 * Normalizes attention weights across verses based on global frequency resonance.
 */
export declare function calculateAttention(verses: string[]): number[];
