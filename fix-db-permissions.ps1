# Fix Database Permissions Script
# This script connects to the server and fixes the SQLite database permissions

Write-Host "🔧 Fixing database permissions on server..." -ForegroundColor Yellow

# Execute commands directly via SSH
Write-Host "📡 Connecting to server and fixing database permissions..." -ForegroundColor Yellow

ssh -i "C:\Users\BenAn\Downloads\LightSailDjango.pem" bitnami@98.87.71.5 @'
cd /opt/bitnami/projects/thecied.dev

# Make sure the database file exists and is writable
if [ -f "db.sqlite3" ]; then
    echo "Found db.sqlite3, fixing permissions..."
    sudo chown daemon:daemon db.sqlite3
    sudo chmod 664 db.sqlite3
    echo "Database file permissions updated"
else
    echo "Database file not found, creating it..."
    python3 manage.py migrate
    sudo chown daemon:daemon db.sqlite3
    sudo chmod 664 db.sqlite3
    echo "Database created and permissions set"
fi

# Also fix the directory permissions
sudo chown daemon:daemon .
sudo chmod 775 .

echo "Database permissions fixed successfully!"
'@

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database permissions fixed successfully!" -ForegroundColor Green
    Write-Host "🔄 Restarting Apache..." -ForegroundColor Yellow
    
    # Restart Apache to apply changes
    ssh -i "C:\Users\BenAn\Downloads\LightSailDjango.pem" bitnami@98.87.71.5 "sudo /opt/bitnami/ctlscript.sh restart apache"
    
    Write-Host "✅ Apache restarted. Try logging into the admin panel now!" -ForegroundColor Green
    Write-Host "🌐 Admin URL: https://thecied.dev/admin/" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to fix database permissions. Check the output above." -ForegroundColor Red
}
