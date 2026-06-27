# Evaluation Report

## Accuracy Metrics
- **claim_status_accuracy**: 70.00%
- **issue_type_accuracy**: 40.00%
- **object_part_accuracy**: 0.00%
- **severity_accuracy**: 10.00%
- **evidence_standard_met_accuracy**: 80.00%
- **risk_flags_accuracy**: 10.00%

## Error Analysis

### Claim Status Discrepancies
- **user_002**: predicted `contradicted` but expected `not_enough_information`
- **user_007**: predicted `contradicted` but expected `supported`
- **user_005**: predicted `not_enough_information` but expected `contradicted`
- **user_030**: predicted `not_enough_information` but expected `supported`
- **user_033**: predicted `not_enough_information` but expected `contradicted`
- **user_034**: predicted `supported` but expected `contradicted`

### Issue Type Discrepancies
- **user_004**: predicted `glass_shatter` but expected `crack`
- **user_007**: predicted `glass_shatter` but expected `broken_part`
- **user_005**: predicted `dent` but expected `scratch`
- **user_006**: predicted `none` but expected `unknown`
- **user_008**: predicted `dent` but expected `broken_part`
- **user_009**: predicted `glass_shatter` but expected `crack`
- **user_011**: predicted `water_damage` but expected `stain`
- **user_018**: predicted `glass_shatter` but expected `crack`
- **user_020**: predicted `scratch` but expected `none`
- **user_032**: predicted `missing_part` but expected `unknown`
- **user_033**: predicted `dent` but expected `unknown`
- **user_034**: predicted `torn_packaging` but expected `none`
