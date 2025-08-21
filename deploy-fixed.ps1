# Deploy Frontend to AWS Lightsail
# This script uploads the Django project with integrated React frontend

$SERVER = "bitnami@thecied.dev"
$PEM_FILE = "C:\Users\BenAn\Downloads\LightSailDjango.pem"
$LOCAL_PATH = "C:\Users\BenAn\Desktop\Playground\thecied.dev"
$REMOTE_PATH = "/home/bitnami/thecied"

Write-Host "Deploying React Frontend + Django Backend to AWS Lightsail..." -ForegroundColor Green

# Step 1: Fix permissions on remote server
Write-Host "Fixing permissions on remote server..." -ForegroundColor Yellow
ssh -i $PEM_FILE $SERVER 'sudo chown -R bitnami:bitnami /home/bitnami/thecied'

# Step 2: Upload project files
Write-Host "Uploading project files..." -ForegroundColor Yellow
scp -i $PEM_FILE -r $LOCAL_PATH/* ${SERVER}:${REMOTE_PATH}/

# Step 3: Set up and restart services
Write-Host "Setting up services on server..." -ForegroundColor Yellow
ssh -i $PEM_FILE $SERVER @'
cd /home/bitnami/thecied

# Install any missing dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Restart Apache
sudo /opt/bitnami/ctlscript.sh restart apache

echo "Deployment complete!"
echo "Visit: https://thecied.dev"
'@

Write-Host "Frontend deployment completed!" -ForegroundColor Green
Write-Host "Your React app should now be live at: https://thecied.dev" -ForegroundColor Cyan
