<!-- Pull Request template translated to English below -->

# Pull Request Template

## PR Type
Please indicate the type of this PR:

- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Documentation
- [ ] Style
- [ ] Performance
- [ ] Config/Build
- [ ] Test
- [ ] LLM Adapter Integration

## Description

### Summary of changes
<!-- Brief summary of main changes -->

### Details
<!-- Detailed description of changes -->

### Related issue
<!-- If this PR closes an issue, link it: Fixes #issue_number -->

## LLM Adapter Integration Checklist (if applicable)

If this PR involves adding or updating an LLM adapter, please complete this checklist. Otherwise you can skip.

### Implementation
- [ ] Adapter class implemented (inherits from OpenAICompatibleBase)
- [ ] provider_name, api_key_env_var, base_url configured
- [ ] Model configuration implemented

### Registration & Integration
- [ ] Registered in OPENAI_COMPATIBLE_PROVIDERS
- [ ] Exported in package __init__.py
- [ ] Added provider option in frontend sidebar

### Environment
- [ ] .env.example updated with example API key
- [ ] Env var naming follows {PROVIDER}_API_KEY
- [ ] base_url configuration provided

## Testing & Validation

### Basic tests
- [ ] API connectivity verified
- [ ] Simple text generation works
- [ ] Error handling in place

### Tool calling tests
- [ ] Function calling works
- [ ] Tool parameter parsing correct
- [ ] Complex tool-call scenarios stable

### Integration tests
- [ ] Frontend displays as expected
- [ ] Model selector works
- [ ] TradingGraph integration succeeds
- [ ] End-to-end analysis flow works

### Performance & Stability
- [ ] Response latency reasonable (< 30s)
- [ ] Long-run stability (> 30 minutes)
- [ ] Memory usage stable
- [ ] Concurrency handling validated

## Documentation & Configuration

### Code documentation
- [ ] Adapter includes docstrings
- [ ] Key methods commented
- [ ] Parameters documented

### User documentation
- [ ] Relevant user guides updated (if needed)
- [ ] Configuration examples provided
- [ ] Troubleshooting notes included (if applicable)

## Test Report (LLM adapter PRs)

Provider info:
- Name:
- Website:
- API docs:
- Supported models:

Test results:
- Basic connectivity: ✅/❌
- Tool calling: ✅/❌
- Web integration: ✅/❌
- E2E: ✅/❌

Performance metrics:
- Avg. latency: ___ s
- Tool success rate: ___%
- Memory usage: ___ MB

Known issues:
<!-- list any known limitations -->

## How to test
<!-- Provide test steps -->
1.
2.
3.

## Test environment
- [ ] Local dev
- [ ] Docker
- [ ] Production

## Breaking changes
- [ ] This PR contains breaking changes
- [ ] This PR does not contain breaking changes

If breaking, provide migration notes:
<!-- migration guidance -->

## Impacted components
Mark affected components:
- [ ] Core trading logic
- [ ] LLM adapters
- [ ] Web UI
- [ ] Data ingestion
- [ ] Config system
- [ ] Test framework
- [ ] Documentation
- [ ] Deployment

## Links
- Documentation:
- References:
- Related PRs:

## Screenshots / Demos
<!-- If UI changes, include screenshots or demo video -->

## Checklist
Code quality:
- [ ] Follows coding style
- [ ] No leftover debug code
- [ ] Clear names and intent
- [ ] Avoids duplicated logic

Testing:
- [ ] New features have tests
- [ ] All tests pass
- [ ] Manual test completed
- [ ] Edge cases considered

Documentation:
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Changelog updated (if needed)
- [ ] Config docs updated (if needed)

Security:
- [ ] No hard-coded secrets
- [ ] Input validation in place
- [ ] Error handling does not leak secrets
- [ ] Third-party deps are trusted

Performance:
- [ ] No major perf regressions
- [ ] Memory usage reasonable
- [ ] Network requests optimized
- [ ] DB queries optimized (if applicable)

## Suggested labels
- [ ] enhancement
- [ ] bug
- [ ] documentation
- [ ] refactor
- [ ] performance
- [ ] security
- [ ] llm-adapter
- [ ] ui/ux
- [ ] config
- [ ] testing

## Reviewers
Suggested reviewers:
<!-- @mention reviewers -->

## Additional notes
<!-- Anything else reviewers should know -->

---

Thank you for your contribution! 🎉

Please ensure you followed the LLM integration guide: ../docs/LLM_INTEGRATION_GUIDE.md