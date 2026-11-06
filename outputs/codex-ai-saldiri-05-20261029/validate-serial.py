import sys
sys.path.insert(0,r'C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools')
import validate
sys.argv=['validate.py','--yol','ai-saldiri']
validate.run_jobs=lambda jobs: [validate.run_job(job) for job in jobs]
raise SystemExit(validate.main())
