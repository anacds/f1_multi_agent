#!/bin/bash

echo "🏁 Iniciando F1 Multi-Agent System..."

# Verificar se os arquivos .env existem em cada serviço
echo "🔍 Verificando arquivos .env dos serviços..."

services=("f1_race_engineer" "f1_tyre_agent" "f1_weather_agent" "f1_tyre_mcp" "f1_weather_mcp")
missing_envs=()

for service in "${services[@]}"; do
    if [ ! -f "$service/.env" ]; then
        missing_envs+=("$service")
        echo "❌ $service/.env não encontrado"
    else
        echo "✅ $service/.env encontrado"
    fi
done

if [ ${#missing_envs[@]} -gt 0 ]; then
    echo ""
    echo "📋 Arquivos .env ausentes encontrados!"
    echo "Copie os arquivos de exemplo e configure as variáveis:"
    echo ""
    for service in "${missing_envs[@]}"; do
        echo "   cp $service/env.example $service/.env"
        echo "   nano $service/.env"
    done
    echo ""
    echo "💡 Dica: Cada serviço tem suas próprias variáveis de ambiente"
    exit 1
fi

echo "✅ Todos os arquivos .env encontrados"

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar todos os serviços
echo "🔨 Construindo e iniciando todos os serviços..."
docker-compose up --build -d

# Aguardar todos os serviços ficarem saudáveis
echo "⏳ Aguardando todos os serviços ficarem saudáveis..."
sleep 30

# Verificar status dos serviços
echo "📊 Status dos serviços:"
docker-compose ps

echo ""
echo "🎉 F1 Multi-Agent System iniciado com sucesso!"
echo ""
echo "📡 Endpoints disponíveis:"
echo "   🎯 Supervisor (Principal): http://localhost:8000"
echo "   🛞 Tyre Agent: http://localhost:8891"
echo "   🌤️  Weather Agent: http://localhost:8892"
echo "   🔧 Tyre MCP: http://localhost:8787"
echo "   🌦️  Weather MCP: http://localhost:8989"
echo ""
echo "📋 Para ver os logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar:"
echo "   docker-compose down"
