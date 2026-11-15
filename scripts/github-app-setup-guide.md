# Connecting Coolify to GitHub: Complete Guide for All VPS Nodes

To allow Coolify to access and auto-deploy all repositories from your GitHub account (`tarikk786786`) to any and all VPS nodes, you install the **Coolify GitHub App**.

---

## 1. Why GitHub App is Recommended
- **Granular Permissions**: No need to provide full personal access tokens.
- **Instant Webhooks**: Coolify automatically listens for `git push` events and auto-deploys within seconds.
- **Multi-Server Targeting**: A single GitHub App connection works across **all VPS servers** registered in your Coolify dashboard.
- **Zero Token Expiry**: Unlike classic PAT tokens that expire, the GitHub App maintains continuous authentication.

---

## 2. Step-by-Step GitHub App Setup in Coolify

### Step 1: Open Your Primary Coolify Dashboard
1. Navigate to `http://<YOUR_PRIMARY_VPS_IP>:8000` (or your custom domain like `https://coolify.tarikislam.in`).
2. Log in with your admin credentials.

### Step 2: Navigate to Sources
1. In the left navigation menu, click **Sources** (or the Cloud icon).
2. Click **+ Add Source** and select **GitHub App**.

### Step 3: Automatically Register the GitHub App
1. Coolify provides an automated GitHub App creation wizard.
2. Enter an App Name (e.g., `Tarik-Coolify-Deployer`).
3. Click **Register GitHub App**.
4. You will be redirected to GitHub (`github.com/settings/apps/new`).
5. GitHub will prefill:
   - App Name
   - Webhook URL (`http://<YOUR_COOLIFY_IP>:8000/webhooks/source/github/events`)
   - Permissions (Repository read/write, Webhooks, Deployments)
6. Scroll to the bottom and click **Create GitHub App**.
7. GitHub will redirect you back to Coolify with the keys and credentials automatically saved!

### Step 4: Install the GitHub App on Your Account
1. Once back in Coolify, click **Install GitHub App**.
2. GitHub will ask: **Where do you want to install this app?**
   - Select your personal account: **tarikk786786**.
3. Choose repository access:
   - **All repositories** (recommended for full automation across all projects), OR
   - **Only select repositories**.
4. Click **Install & Authorize**.

---

## 3. Connecting All Your VPS Servers in Coolify

Once the GitHub App is installed, you can add any number of additional VPS servers into Coolify:

1. In Coolify, go to **Servers** -> **+ Add Server**.
2. Enter:
   - **Server Name**: e.g. `Oracle-Free-Tier-1`, `Hetzner-Worker`, `Contabo-DB`.
   - **IP Address**: Public IPv4 of the VPS.
   - **Port**: `22` (or your custom SSH port).
   - **User**: `root` (or `ubuntu` / `admin`).
   - **SSH Private Key**: Select or paste your private key.
3. Click **Validate & Save**.
4. Coolify connects to the remote VPS, tests Docker, installs the Coolify helper container, and marks the server as **Healthy**.

---

## 4. Deploying Any GitHub Repo to Any VPS

Now you can deploy any project:
1. Go to **Projects** -> **+ Add Project**.
2. Click **+ New Resource** -> **Application** -> **GitHub**.
3. Pick your GitHub App (`tarikk786786`).
4. Select your repository (e.g. `tarikk786786/mark-lvi` or any app).
5. **Select Destination Server**: Choose **any of your registered VPS servers** from the dropdown!
6. Click **Deploy**. Coolify builds the Docker container and deploys it with automated SSL!
