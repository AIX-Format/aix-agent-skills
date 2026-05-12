# Test Tool — TIER: BASIC_TOOL

## What
A minimal validation tool for testing AIX skill integration and functionality.

## Core Functions
- **Skill Validation**: Tests if a skill follows AIX manifest schema
- **API Testing**: Validates API route patterns and responses
- **Constitutional Testing**: Ensures skills respect constitutional boundaries
- **Performance Testing**: Measures execution time and resource usage

## Test Categories

### 1. Schema Validation
```typescript
interface TestResult {
  skillName: string;
  passed: boolean;
  errors: string[];
  warnings: string[];
  duration: number;
}
```

### 2. API Route Testing
- Validates standard API patterns under `/api/agents/[id]/`
- Tests GET/POST/PUT/DELETE operations
- Checks response formats and error handling

### 3. Constitutional Compliance
- Tests against purity-filter rules
- Validates trust-chain integration
- Ensures proper tier enforcement

### 4. Integration Testing
- Tests skill-to-skill communication
- Validates memory system integration
- Checks proper error propagation

## Usage Example
```bash
# Test single skill
npm run test:skill -- agent-memory

# Test all skills
npm run test:all

# Test with specific tier
npm run test:tier -- PRO
```

## Success Criteria
- All schema validations pass
- API responses conform to standards
- Constitutional checks succeed
- Performance metrics within acceptable ranges

## Integration
Works with the CI/CD pipeline to prevent deployment of broken skills.
