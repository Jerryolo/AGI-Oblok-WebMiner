# Plan wdrożenia

1. **Dni 1–2:** threat model, właściciel procesu, klucze HSM/secret manager, OIDC/mTLS.
2. **Dni 3–7:** 14-dniowy shadow, corpus adversarial, baseline metryk i eksport WORM.
3. **Dni 8–14:** advisory, szkolenie operatorów STOP, ćwiczenie incydentu i restore.
4. **Go-live:** canary enforcing, limity ruchu, alarmy 5xx/tamper/REJECT, formalna akceptacja.

Frontend publikuje GitHub Actions do Cloudflare Pages jako `gate.neonai.shop`. Backend należy uruchomić na VPS/Kubernetes za TLS/WAF; Worker może pełnić edge proxy, lecz Python API i trwały audit pozostają w zaufanej strefie. Sekrety `CLOUDFLARE_*`, `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` przechowuje GitHub Environments. Rollback wskazuje poprzedni obraz; pliku audytu nigdy się nie cofa.
