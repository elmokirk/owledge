# Team Evaluation Checklist

Use this before adopting Owledge in a team or client project.

| Check | Pass condition |
| --- | --- |
| Repository access | The repo or vault already has access control. |
| Data classification | Team knows which files may contain personal or customer data. |
| Runtime hooks | Team decides whether private capture is needed. |
| Shared export | Team approves review and sanitization policy. |
| Retention | Team owns deletion and retention procedures. |
| Incident path | Team knows how to handle accidental secret or customer-data commits. |
| Rollout | First adoption uses synthetic or non-customer data. |

## Recommended First Rollout

1. Run the launch demo.
2. Add Owledge to one internal repo.
3. Keep runtime hooks off unless needed.
4. Run validation before any RAG export.
5. Review one handoff and one evidence file with the team.

