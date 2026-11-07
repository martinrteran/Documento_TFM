# Genera los PNG de las figuras TikZ (escena POMDP y modelos cinemáticos),
# cada una con ejes c/r y x/y.
# Uso, desde la raíz del documento:  powershell -File imagenes\tikz\generar_png.ps1
$raiz = Resolve-Path "$PSScriptRoot\..\.."
$tmp = Join-Path $env:TEMP "tfm_tikz_png"
New-Item -ItemType Directory -Force $tmp | Out-Null
$figuras = @{
    "pomdp-escena"        = "POMDP_Escena"
    "cinematica-sin-giro" = "Cinematica_SinGiro"
    "cinematica-con-giro" = "Cinematica_ConGiro"
}
$ejes = @(@{ h = "c"; v = "r"; sufijo = "cr" }, @{ h = "x"; v = "y"; sufijo = "xy" })
Push-Location $raiz
try {
    foreach ($fig in $figuras.Keys) {
        foreach ($e in $ejes) {
            $job = "$($figuras[$fig])_$($e.sufijo)"
            $cmd = "\def\figura{$fig}\def\ejeH{$($e.h)}\def\ejeV{$($e.v)}\input{imagenes/tikz/png-standalone}"
            pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$tmp" -jobname="$job" $cmd | Out-Null
            if ($LASTEXITCODE -ne 0) { Write-Error "Fallo al compilar $job (ver $tmp\$job.log)"; continue }
            pdftoppm -png -r 300 -singlefile "$tmp\$job.pdf" "imagenes\$job"
            Write-Output "imagenes\$job.png"
        }
    }
}
finally { Pop-Location }
