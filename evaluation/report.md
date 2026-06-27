# Evaluation Report

## Accuracy Metrics

- **claim_status_accuracy**: 75.00%
- **issue_type_accuracy**: 100.00%
- **object_part_accuracy**: 100.00%
- **severity_accuracy**: 85.00%
- **evidence_standard_met_accuracy**: 80.00%
- **risk_flags_accuracy**: 100.00%

## Error Analysis

### Claim Status Discrepancies

- **user_002**: predicted `supported` but expected `not_enough_information`
- **user_005**: predicted `supported` but expected `contradicted`
- **user_006**: predicted `contradicted` but expected `not_enough_information`
- **user_008**: predicted `not_enough_information` but expected `contradicted`
- **user_032**: predicted `contradicted` but expected `not_enough_information`

## Operational Analysis

### Model Calls

- **Sample set (20 claims):** 20 text‑only calls (claim parser) + 30 vision calls (one per image).
- **Full test set (approx. 40 claims, ~60 images):** 40 text calls + 60 vision calls.

### Token Usage (estimated per call)

- **Claim Parser:** Input ~500 tokens (user conversation), output ~50 tokens.
- **Visual Analyzer:** Input (text portion) ~200 tokens, output ~150 tokens (JSON). Image processing is charged per image, not per token.

### Images Processed

- **Sample set:** 30 images.
- **Full test set:** ~60 images (averaging 1.5 images per claim).

### Pricing Assumptions (Gemini 2.5 Flash, approximated from Gemini 1.5 Flash pricing)

- Text: $0.0000025 per 1k input tokens, $0.0000075 per 1k output tokens.
- Vision: $0.00002 per image (flat fee) + text token costs for the prompt.

### Cost Estimate

**Sample set (20 claims, 30 images):**  
Text input: 20 × 500 tokens = 10k tokens → $0.025  
Text output: 20 × 50 tokens = 1k tokens → $0.0075  
Vision (images): 30 × $0.00002 = $0.0006  
**Total sample cost ≈ $0.033**

**Full test set (40 claims, 60 images):**  
Text input: 40 × 500 tokens = 20k tokens → $0.050  
Text output: 40 × 50 tokens = 2k tokens → $0.015  
Vision: 60 × $0.00002 = $0.0012  
**Total test cost ≈ $0.066**

> Actual costs may vary slightly with conversation length and image complexity.

### Latency / Runtime

- Each text call takes ~1‑2 seconds; each vision call ~2‑5 seconds.
- On a single‑threaded run, processing 40 claims with 60 images takes roughly **3‑5 minutes** (dominated by vision calls).
- With parallel vision processing (future enhancement), runtime can drop to **< 1 minute**.

### TPM / RPM Considerations

- Gemini free tier limits: **10 requests per minute (RPM)** and **60 requests per minute** for pay‑as‑you‑go.
- Our pipeline processes claims sequentially, with no artificial throttling beyond the built‑in `tenacity` retry (which adds backoff only on errors).
- No batching is used for API calls (each image sent individually).
- Retry strategy: 3 attempts with exponential backoff (4‑60 s) on transient errors (`ResourceExhausted`, `ServiceUnavailable`, `DeadlineExceeded`).
- Optional `DiskCache` caching can eliminate duplicate image analyses across re‑runs.

### Strategies for Production

- Enable `services/cache.py` to cache vision results per image hash + claim context.
- Parallelise vision calls with `concurrent.futures.ThreadPoolExecutor` for higher throughput.
- Monitor RPM via logging and insert artificial delays if nearing the free‑tier limit.
