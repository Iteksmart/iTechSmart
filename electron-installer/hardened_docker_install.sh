#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.production.yml"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"
ENV_FILE="$PROJECT_ROOT/.env"
INSTALL_LOG="$PROJECT_ROOT/install.log"

print() { 
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$INSTALL_LOG"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

prompt_yes_no() {
  local prompt="$1"
  read -r -p "$prompt [Y/n]: " ans
  ans=${ans:-Y}
  [[ "$ans" =~ ^([yY]) ]]
}

check_prerequisites() {
  local missing=()
  for cmd in curl sudo; do
    if ! command_exists "$cmd"; then
      missing+=("$cmd")
    fi
  done
  
  if [ ${#missing[@]} -gt 0 ]; then
    print "ERROR: Missing required commands: ${missing[*]}"
    exit 1
  fi
}

ensure_root() {
  if [ "$EUID" -ne 0 ]; then
    print "Some steps require sudo. You will be prompted when needed."
  fi
}

install_docker() {
  if command_exists docker; then
    print "Docker already installed."
    return
  fi

  print "Installing Docker (using official convenience script)..."
  local script="/tmp/get-docker.sh"
  
  curl -fsSL https://get.docker.com -o "$script"
  print "Docker install script downloaded to $script"
  
  if prompt_yes_no "Review script before running? (Recommended)"; then
    ${PAGER:-less} "$script"
  fi
  
  if prompt_yes_no "Proceed with Docker installation?"; then
    sudo sh "$script"
    rm -f "$script"
    
    print "Docker installed."
    print "WARNING: Adding user to 'docker' group grants root-equivalent privileges."
    
    if prompt_yes_no "Add current user ($USER) to docker group?"; then
      sudo usermod -aG docker "$USER"
      print "User added to docker group. You MUST log out and back in for this to take effect."
      print "Alternative: Use 'sudo docker' for commands in current session."
    fi
  else
    print "Docker installation cancelled."
    exit 1
  fi
}

install_docker_compose() {
  if command_exists docker-compose || command_exists docker compose; then
    print "Docker Compose already available."
    return
  fi

  print "Installing docker-compose-plugin..."
  sudo apt-get update || true
  sudo apt-get install -y docker-compose-plugin || true
  
  if ! command_exists docker compose && ! command_exists docker-compose; then
    print "Installing standalone docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
  fi
  print "Docker Compose installed."
}

prepare_env() {
  if [ -f "$ENV_FILE" ]; then
    print ".env already exists; leaving it in place."
    return
  fi
  
  if [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    print "Copied .env.example -> .env with secure permissions (600)."
    print "IMPORTANT: Edit $ENV_FILE to set secrets and production values before starting."
  else
    print "No .env.example found; creating empty .env."
    touch "$ENV_FILE"
    chmod 600 "$ENV_FILE"
  fi
}

wait_for_healthy() {
  print "Waiting for containers to be healthy (timeout: 60s)..."
  local max_wait=60
  local elapsed=0
  
  while [ $elapsed -lt $max_wait ]; do
    local unhealthy
    unhealthy=$(docker ps --filter "health=unhealthy" --filter "label=com.docker.compose.project" -q 2>/dev/null | wc -l)
    local starting
    starting=$(docker ps --filter "health=starting" --filter "label=com.docker.compose.project" -q 2>/dev/null | wc -l)
    
    if [ "$unhealthy" -eq 0 ] && [ "$starting" -eq 0 ]; then
      print "All containers healthy!"
      return 0
    fi
    
    sleep 5
    elapsed=$((elapsed + 5))
  done
  
  print "WARNING: Some containers may not be healthy yet. Check with: docker compose ps"
}

bring_up_compose() {
  if [ ! -f "$COMPOSE_FILE" ]; then
    print "ERROR: $COMPOSE_FILE not found."
    exit 1
  fi

  print "Starting Docker Compose stack..."
  
  if command_exists docker && docker compose version >/dev/null 2>&1; then
    docker compose -f "$COMPOSE_FILE" up -d --remove-orphans
  elif command_exists docker-compose; then
    docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
  else
    print "ERROR: No docker compose command available."
    exit 1
  fi

  wait_for_healthy
  
  print ""
  print "Container status:"
  docker ps --filter "label=com.docker.compose.project" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --skip-docker    Skip installing Docker
  --skip-compose   Skip starting docker-compose stack
  -h, --help       Show this help message

Installation log: $INSTALL_LOG
EOF
}

main() {
  print "=== Installation started ==="
  
  check_prerequisites
  ensure_root

  SKIP_DOCKER=0
  SKIP_COMPOSE=0

  while [ $# -gt 0 ]; do
    case "$1" in
      --skip-docker) SKIP_DOCKER=1 ;;
      --skip-compose) SKIP_COMPOSE=1 ;;
      -h|--help) usage; exit 0 ;;
      *) print "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
  done

  if [ $SKIP_DOCKER -eq 0 ]; then
    install_docker
    install_docker_compose
  fi

  prepare_env

  if [ $SKIP_COMPOSE -eq 0 ]; then
    if [ ! -f "$ENV_FILE" ] || [ ! -s "$ENV_FILE" ]; then
      print "WARNING: .env file is empty or missing."
      if ! prompt_yes_no "Continue anyway? (Not recommended)"; then
        print "Please populate $ENV_FILE and run again."
        exit 1
      fi
    fi
    
    if prompt_yes_no "Start Docker Compose stack now?"; then
      bring_up_compose
      print ""
      print "✓ Docker Compose deployment completed."
      print ""
      print "Next steps:"
      print "  - View logs: docker compose -f $COMPOSE_FILE logs -f"
      print "  - Check status: docker compose -f $COMPOSE_FILE ps"
      print "  - Stop stack: docker compose -f $COMPOSE_FILE down"
    else
      print "Skipping starting stack."
    fi
  fi

  print "=== Installation complete ==="
  print "Full log available at: $INSTALL_LOG"
}

main "$@"