# 🏁 F1 Multi-Agent System - Docker Setup

Este projeto implementa um sistema multi-agente para simulação de estratégias de Fórmula 1 usando Docker.

## 🚀 Início Rápido

### 1. Pré-requisitos
- Docker e Docker Compose instalados
- Chave da API OpenAI
- Chave da API AccuWeather (opcional, para funcionalidade completa)

### 2. Configuração
```bash
# Clone o repositório
git clone <seu-repositorio>
cd f1_multi_agent

# Copie os arquivos de exemplo para cada serviço
cp f1_race_engineer/env.example f1_race_engineer/.env
cp f1_tyre_agent/env.example f1_tyre_agent/.env
cp f1_weather_agent/env.example f1_weather_agent/.env
cp f1_tyre_mcp/env.example f1_tyre_mcp/.env
cp f1_weather_mcp/env.example f1_weather_mcp/.env

# Edite cada arquivo .env com suas chaves de API
nano f1_race_engineer/.env
nano f1_tyre_agent/.env
nano f1_weather_agent/.env
nano f1_tyre_mcp/.env
nano f1_weather_mcp/.env
```

### 3. Executar
```bash
# Tornar o script executável
chmod +x start.sh

# Iniciar todos os serviços
./start.sh
```

## 📁 Estrutura de Arquivos .env

Cada serviço tem seu próprio arquivo `.env` com variáveis específicas:

```
f1_multi_agent/
├── f1_race_engineer/.env      # Supervisor (orquestrador)
├── f1_tyre_agent/.env         # Agente de pneus
├── f1_weather_agent/.env      # Agente de clima
├── f1_tyre_mcp/.env           # Servidor MCP de pneus
└── f1_weather_mcp/.env        # Servidor MCP de clima
```

### Variáveis Obrigatórias por Serviço:

- **Todos os agentes**: `OPENAI_API_KEY`
- **Weather MCP**: `ACCUWEATHER_API_KEY` (opcional)
- **Cada serviço**: Suas próprias configurações de porta e host

## 🐳 Serviços Disponíveis

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **Supervisor** | 8000 | Orquestrador principal |
| **Tyre Agent** | 8891 | Agente especializado em pneus |
| **Weather Agent** | 8892 | Agente especializado em clima |
| **Tyre MCP** | 8787 | Servidor MCP para pneus |
| **Weather MCP** | 8989 | Servidor MCP para clima |

## 🔧 Comandos Úteis

### Gerenciamento de Serviços
```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f supervisor
```

### Desenvolvimento
```bash
# Reconstruir um serviço específico
docker-compose build supervisor

# Executar comando em um container
docker-compose exec supervisor bash

# Ver status dos serviços
docker-compose ps
```

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐
│   Supervisor    │    │   Tyre Agent    │
│   (Port 8000)   │◄──►│   (Port 8891)   │
└─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         │              │   Tyre MCP      │
         │              │   (Port 8787)   │
         │              └─────────────────┘
         │
┌─────────────────┐    ┌─────────────────┐
│ Weather Agent   │    │   Weather MCP   │
│   (Port 8892)   │◄──►│   (Port 8989)   │
└─────────────────┘    └─────────────────┘
```

## 🔍 Health Checks

Todos os serviços incluem health checks automáticos:
- Verificação a cada 30 segundos
- Timeout de 10 segundos
- 3 tentativas antes de falhar
- Período de inicialização de 40 segundos

## 🐛 Troubleshooting

### Problemas Comuns

1. **Serviços não iniciam**
   ```bash
   # Verificar logs
   docker-compose logs
   
   # Verificar se as portas estão livres
   netstat -tulpn | grep :8000
   ```

2. **Erro de API Key**
   ```bash
   # Verificar se o arquivo .env está correto
   cat .env
   
   # Verificar se as variáveis estão sendo carregadas
   docker-compose exec supervisor env | grep OPENAI
   ```

3. **Serviços não se comunicam**
   ```bash
   # Verificar rede Docker
   docker network ls
   docker network inspect f1_multi_agent_f1-network
   ```

### Logs Detalhados
```bash
# Logs de todos os serviços
docker-compose logs

# Logs de um serviço específico
docker-compose logs supervisor
docker-compose logs tyre-agent
docker-compose logs weather-agent
```

## 📊 Monitoramento

### Verificar Status
```bash
# Status dos containers
docker-compose ps

# Uso de recursos
docker stats

# Health checks
docker-compose exec supervisor curl http://localhost:8000/health
```

## 🔄 Atualizações

```bash
# Parar serviços
docker-compose down

# Reconstruir imagens
docker-compose build --no-cache

# Iniciar novamente
docker-compose up -d
```

## 🧹 Limpeza

```bash
# Parar e remover containers
docker-compose down

# Remover imagens
docker-compose down --rmi all

# Limpeza completa (cuidado!)
docker system prune -a
```
