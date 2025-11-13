# API Types Automation

## Overview

The backend automatically generates and syncs TypeScript types to the frontend repository whenever the OpenAPI schema changes.

## Workflow: openapi-schema.yml

### Triggers
- Push to `main` branch
- Pull requests to `main`
- Manual dispatch

### Jobs

#### 1. export-schema
Runs on all triggers (PR and main branch).

**Steps:**
1. Export OpenAPI schema from FastAPI app to `backend/openapi.json`
2. Validate the schema is valid JSON
3. Upload as workflow artifact (retention: 90 days)
4. (PR only) Comment on PR with endpoint list

#### 2. generate-typescript
Runs only on **main branch pushes** (after export-schema).

**Steps:**
1. Checkout both backend and frontend repositories
2. Download OpenAPI schema artifact
3. Generate TypeScript types using `openapi-typescript`
4. **Commit to backend:** Save types to `backend/api-types.ts`
5. **Sync to frontend:** Copy types to `frontend-repo/src/lib/generated/api-types.ts`
6. **Commit to frontend:** Push updated types to frontend repository
7. Upload types as artifact

### Permissions Required

```yaml
permissions:
  contents: write  # Required to commit generated files
  pull-requests: write  # Required for PR comments
  issues: write  # Required for PR comments
```

### Secrets

**FRONTEND_SYNC_TOKEN** (optional but recommended)
- **Purpose:** Allows pushing commits to the frontend repository
- **Type:** GitHub Personal Access Token (Classic) or Fine-grained token
- **Required scopes:**
  - `repo` (full control of private repositories)
  - Or `contents: write` for fine-grained tokens
- **Fallback:** Uses default `github.token` if not provided (may have limited permissions)

#### Creating the Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic) with `repo` scope
3. Copy the token
4. Add to repository secrets as `FRONTEND_SYNC_TOKEN`

## Generated Files

### backend/openapi.json
Complete OpenAPI 3.0 schema exported from FastAPI.

**Usage:**
- Consumed by openapi-typescript for type generation
- Available as workflow artifact
- Can be used for API documentation tools (Swagger UI, Redoc, etc.)

### backend/api-types.ts
TypeScript type definitions generated from OpenAPI schema.

**Format:**
```typescript
export interface paths {
  '/api/tokens/history': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': TokensResponse;
          };
        };
      };
    };
  };
  // ...
}

export interface components {
  schemas: {
    Token: {
      id: number;
      token_address: string;
      // ...
    };
    // ...
  };
}
```

**Location in frontend:** Copied to `src/lib/generated/api-types.ts`

## Integration with Frontend

The frontend repository has a CI guard that ensures types stay in sync:

```yaml
# frontend/.github/workflows/ci.yml
api-types-check:
  name: API Types Sync Check
  runs-on: ubuntu-latest
  steps:
    - name: Checkout frontend repo
    - name: Checkout backend repo
    - name: Generate types from backend schema
    - name: Compare with committed types
    # Fails if out of sync
```

See frontend repository's `.github/API_TYPES_SYNC.md` for complete documentation.

## Testing Locally

### Generate OpenAPI Schema

```bash
cd backend
python <<'PYEOF'
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from app.main import app
schema = app.openapi()
with open('openapi.json', 'w') as f:
    json.dump(schema, f, indent=2)
PYEOF
```

### Generate TypeScript Types

```bash
# Install openapi-typescript globally
npm install -g openapi-typescript

# Generate types
npx openapi-typescript backend/openapi.json -o backend/api-types.ts
```

### Manual Sync to Frontend

```bash
# Copy to frontend (adjust path as needed)
cp backend/api-types.ts ../gun-del-sol-web/src/lib/generated/api-types.ts
```

## Commit Messages

The workflow uses standardized commit messages:

**Backend:**
```
chore: update generated TypeScript types from OpenAPI schema
```

**Frontend:**
```
chore: update API types from backend OpenAPI schema

Auto-generated from backend commit <sha>
```

## Troubleshooting

### Workflow Fails: Permission Denied

**Symptom:** "refusing to allow a GitHub App to create or update workflow"

**Cause:** Default `github.token` lacks permissions to push to repositories.

**Solution:** Add `FRONTEND_SYNC_TOKEN` secret with proper permissions.

### Types Not Syncing

**Check:**
1. Workflow only runs on `main` branch - verify you're pushing to main
2. Check workflow run logs for errors
3. Verify frontend repository path in checkout step
4. Ensure frontend repo is accessible with provided token

### Schema Export Fails

**Common causes:**
- Missing config files (`config.json`, `api_settings.json`, `monitored_addresses.json`)
- Python import errors
- FastAPI app initialization issues

**Solution:** Workflow creates test config files automatically. Verify backend dependencies are installed.

## Future Enhancements

- [ ] Add schema versioning and changelog generation
- [ ] Detect breaking changes and require manual approval
- [ ] Generate runtime validation schemas (e.g., zod)
- [ ] Add metrics tracking for schema changes
- [ ] Support multiple API versions

## Related Documentation

- [Frontend API Types Sync](../../gun-del-sol-web/.github/API_TYPES_SYNC.md)
- [OpenAPI Specification](https://swagger.io/specification/)
- [openapi-typescript Documentation](https://github.com/drwpow/openapi-typescript)

---

**Last Updated:** November 2025
**Repository:** [88simon/solscan_hotkey](https://github.com/88simon/solscan_hotkey)
