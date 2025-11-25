# Deployment Instructions

This guide explains how to deploy the Texas Grid Interconnect Reporter to Google Cloud Platform (GCP) using Cloud Run.

## Prerequisites 🚀

### 1. Google Cloud SDK (gcloud CLI) and Authentication

Ensure you have the `gcloud` CLI installed and authenticated.

* [Install gcloud CLI](https://cloud.google.com/sdk/docs/install)
* Run `gcloud auth login` to authenticate with your user account.
* Run `gcloud config set project YOUR_PROJECT_ID` to set your active project.

### 2. Verify and Enable Billing (CRITICAL 💰)

**You must have a billing account linked to your project.** A "Forbidden" error is often caused by missing payment credentials, as Google Cloud cannot provision resources like the Cloud Build staging bucket without billing enabled.

* **Action:** Go to the [Google Cloud Billing page](https://console.cloud.google.com/billing) and ensure your project is linked to an active billing account.

### 3. Enable Required GCP Services

For a new project, you must enable the APIs for building, storing, and deploying.

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    run.googleapis.com

4.  **Grant Required IAM Roles for Cloud Build (CRITICAL)**: To run the `./deploy.sh` script (which uses `gcloud builds submit`), your authenticated user must have permissions to create a build and upload the source code. Execute the following commands, making sure to **replace `YOUR_EMAIL_ADDRESS` and `YOUR_PROJECT_ID`** with your actual user email and project ID.

    ```bash
    # 1. Grant permission to create and manage builds
    gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
        --member="user:YOUR_EMAIL_ADDRESS" \
        --role="roles/cloudbuild.builds.editor"

    # 2. Grant permission to use the Cloud Build service (prevents 'forbidden from accessing the bucket' errors)
    gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
        --member="user:YOUR_EMAIL_ADDRESS" \
        --role="roles/serviceusage.serviceUsageConsumer"
    ```

5.  **GCP Project**: You need a Google Cloud Project with billing enabled.
    *   Enable **Cloud Run API** and **Container Registry API** (or Artifact Registry API).
    *   Run: `gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com`

## Configuration

1.  Open `config.yaml` in the root directory.
2.  Update the `project_id` with your actual GCP project ID.
3.  (Optional) Change `region`, `service_name`, or `image_name` if desired.

```yaml
project_id: "my-gcp-project-id"
region: "us-central1"
service_name: "texas-grid-reporter"
image_name: "texas-grid-reporter"
```

## Deployment

1.  Run the deployment script:

```bash
./deploy.sh
```

This script will:
1.  Read your configuration.
2.  Submit the build to Google Cloud Build (which builds the Docker image remotely).
3.  Push the image to Google Container Registry (GCR).
4.  Deploy the image to Cloud Run.

## Local Development

To run the application locally with the production build process (simulating deployment):

1.  Build the Docker image:
    ```bash
    docker build -t texas-grid-reporter .
    ```
2.  Run the container:
    ```bash
    docker run -p 8080:8080 texas-grid-reporter
    ```
3.  Open `http://localhost:8080` in your browser.

## Architecture

*   **Frontend**: React app (Vite) built into static files.
*   **Backend**: FastAPI (Python) serving the API and the static frontend files.
*   **Infrastructure**: Google Cloud Run (Serverless Container).
