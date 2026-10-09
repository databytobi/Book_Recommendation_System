# ============================================================
# Book Recommendation System — local Docker helper
#
#   .\docker.ps1 up        start the stack (build if needed)
#   .\docker.ps1 build     rebuild images
#   .\docker.ps1 logs      follow API logs
#   .\docker.ps1 status    container health
#   .\docker.ps1 test      quick smoke test of the API
#   .\docker.ps1 shell     shell into the API container
#   .\docker.ps1 down      stop the stack (keeps data)
#   .\docker.ps1 reset     stop and DELETE all data/volumes
#
# The API loads a ~900 MB FAISS index into memory. Expect the first
# startup to take 30-60 seconds before it reports healthy.
# ============================================================

param(
    [Parameter(Position = 0)]
    [ValidateSet('up', 'build', 'logs', 'status', 'test', 'shell', 'down', 'reset', 'ps')]
    [string]$Command = 'up',

    [switch]$Prod
)

$ErrorActionPreference = 'Stop'

# Use the production stack when -Prod is passed, otherwise the dev stack.
$composeFile = if ($Prod) {
    'infrastructure/compose/docker-compose.prod.yml'
} else {
    'infrastructure/compose/docker-compose.dev.yml'
}

function Invoke-Compose {
    param([string[]]$Args)
    & docker compose -f $composeFile @Args
}

function Assert-Docker {
    # Fail with a clear message rather than a named-pipe stack trace.
    & docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker is not reachable. Start Docker Desktop and wait for 'Engine running'." -ForegroundColor Red
        exit 1
    }
}

Assert-Docker

switch ($Command) {

    'up' {
        Write-Host "Starting stack ($composeFile)..." -ForegroundColor Cyan
        Invoke-Compose @('up', '-d', '--build')
        Write-Host ""
        Write-Host "Waiting for the API to become healthy (models load slowly)..." -ForegroundColor Yellow

        $deadline = (Get-Date).AddMinutes(3)
        $healthy = $false
        while ((Get-Date) -lt $deadline) {
            $state = (& docker inspect --format '{{.State.Health.Status}}' book_api 2>$null)
            if ($state -eq 'healthy') { $healthy = $true; break }
            Start-Sleep -Seconds 5
            Write-Host "  ...$state"
        }

        Write-Host ""
        if ($healthy) {
            Write-Host "API is healthy." -ForegroundColor Green
        } else {
            Write-Host "API did not report healthy within 3 minutes. Check: .\docker.ps1 logs" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "  Frontend : http://localhost:3000" -ForegroundColor Green
        Write-Host "  API docs : http://localhost:8000/docs" -ForegroundColor Green
        Write-Host "  API base : http://localhost:8000/api/v1" -ForegroundColor Green
    }

    'build' {
        Invoke-Compose @('build')
    }

    'logs' {
        Invoke-Compose @('logs', '-f', '--tail', '80', 'api')
    }

    'status' {
        Invoke-Compose @('ps')
        Write-Host ""
        Write-Host "Container health:"
        foreach ($c in @('book_api', 'book_frontend', 'book_postgres', 'book_redis')) {
            $s = (& docker inspect --format '{{.State.Status}} / {{if .State.Health}}{{.State.Health.Status}}{{else}}no healthcheck{{end}}' $c 2>$null)
            if ($s) { Write-Host ("  {0,-16} {1}" -f $c, $s) }
        }
    }

    'test' {
        Write-Host "Smoke testing the API..." -ForegroundColor Cyan
        $checks = @(
            @{ Name = 'root'; Url = 'http://localhost:8000/' },
            @{ Name = 'liveness'; Url = 'http://localhost:8000/api/v1/health/liveness' },
            @{ Name = 'readiness'; Url = 'http://localhost:8000/api/v1/health/readiness' },
            @{ Name = 'ml recommender'; Url = 'http://localhost:8000/api/v1/recommendation/health' },
            @{ Name = 'trending'; Url = 'http://localhost:8000/api/v1/recommendation/trending' }
        )
        foreach ($c in $checks) {
            try {
                $r = Invoke-WebRequest -Uri $c.Url -UseBasicParsing -TimeoutSec 60
                Write-Host ("  {0,-16} HTTP {1}" -f $c.Name, $r.StatusCode) -ForegroundColor Green
            } catch {
                $code = $_.Exception.Response.StatusCode.value__
                Write-Host ("  {0,-16} FAILED {1}" -f $c.Name, $code) -ForegroundColor Red
            }
        }
    }

    'shell' {
        Invoke-Compose @('exec', 'api', 'bash')
    }

    'down' {
        Invoke-Compose @('down')
    }

    'reset' {
        Write-Host "This deletes the database, Redis data and cached artifacts." -ForegroundColor Red
        $answer = Read-Host "Type 'yes' to continue"
        if ($answer -eq 'yes') {
            Invoke-Compose @('down', '-v')
            Write-Host "All volumes removed." -ForegroundColor Green
        } else {
            Write-Host "Cancelled."
        }
    }

    'ps' {
        Invoke-Compose @('ps')
    }
}