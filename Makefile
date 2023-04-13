.PHONY:
build_image:
	gcloud builds submit --config vertex/deployment/cloudbuild.yaml