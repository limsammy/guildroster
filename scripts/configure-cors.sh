#!/bin/bash

# Script to configure CORS settings for GuildRoster
# This script helps you set up the correct CORS origins for your deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}GuildRoster CORS Configuration Helper${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Function to add domain to CORS origins
add_domain_to_cors() {
    local domain=$1
    local env_file=${2:-.env}
    
    if [ -f "$env_file" ]; then
        # Check if CORS_ORIGINS already exists
        if grep -q "^CORS_ORIGINS=" "$env_file"; then
            # Check if this is a single domain or comma-separated list
            if [[ "$domain" == *","* ]]; then
                # It's a comma-separated list, replace the entire value
                # Escape dots and other special characters for sed
                escaped_domain=$(echo "$domain" | sed 's/\./\\./g')
                sed -i "s/^CORS_ORIGINS=.*/CORS_ORIGINS=$escaped_domain/" "$env_file"
                echo -e "${GREEN}✓ Updated CORS_ORIGINS with new list in $env_file${NC}"
            else
                # It's a single domain, append to existing
                current_origins=$(grep "^CORS_ORIGINS=" "$env_file" | cut -d'=' -f2-)
                new_origins="$current_origins,$domain"
                # Escape dots in domain for sed replacement
                escaped_current=$(echo "$current_origins" | sed 's/\./\\./g')
                escaped_new=$(echo "$new_origins" | sed 's/\./\\./g')
                sed -i "s/^CORS_ORIGINS=$escaped_current/CORS_ORIGINS=$escaped_new/" "$env_file"
                echo -e "${GREEN}✓ Added $domain to existing CORS_ORIGINS in $env_file${NC}"
            fi
        else
            # Add new CORS_ORIGINS line
            echo "" >> "$env_file"
            echo "# CORS Configuration" >> "$env_file"
            echo "CORS_ORIGINS=$domain" >> "$env_file"
            echo "CORS_ALLOW_CREDENTIALS=true" >> "$env_file"
            echo "CORS_ALLOW_METHODS=*" >> "$env_file"
            echo "CORS_ALLOW_HEADERS=*" >> "$env_file"
            echo -e "${GREEN}✓ Added CORS configuration to $env_file${NC}"
        fi
    else
        echo -e "${RED}✗ Environment file $env_file not found${NC}"
        return 1
    fi
}

# Function to show current CORS configuration
show_cors_config() {
    local env_file=${1:-.env}
    
    if [ -f "$env_file" ]; then
        echo -e "${YELLOW}Current CORS configuration in $env_file:${NC}"
        echo ""
        if grep -q "^CORS_ORIGINS=" "$env_file"; then
            echo -e "${BLUE}CORS_ORIGINS:${NC}"
            grep "^CORS_ORIGINS=" "$env_file" | cut -d'=' -f2- | tr ',' '\n' | sed 's/^/  - /'
            echo ""
        else
            echo -e "${RED}No CORS_ORIGINS configured${NC}"
        fi
        
        if grep -q "^CORS_ALLOW_CREDENTIALS=" "$env_file"; then
            echo -e "${BLUE}CORS_ALLOW_CREDENTIALS:${NC} $(grep "^CORS_ALLOW_CREDENTIALS=" "$env_file" | cut -d'=' -f2)"
        fi
        
        if grep -q "^CORS_ALLOW_METHODS=" "$env_file"; then
            echo -e "${BLUE}CORS_ALLOW_METHODS:${NC} $(grep "^CORS_ALLOW_METHODS=" "$env_file" | cut -d'=' -f2)"
        fi
        
        if grep -q "^CORS_ALLOW_HEADERS=" "$env_file"; then
            echo -e "${BLUE}CORS_ALLOW_HEADERS:${NC} $(grep "^CORS_ALLOW_HEADERS=" "$env_file" | cut -d'=' -f2)"
        fi
    else
        echo -e "${RED}Environment file $env_file not found${NC}"
    fi
}

# Function to generate CORS origins for a domain
generate_cors_origins() {
    local domain=$1
    local origins=""
    
    # Add HTTP and HTTPS versions
    origins="$origins,http://$domain"
    origins="$origins,https://$domain"
    
    # Add www subdomain versions
    origins="$origins,http://www.$domain"
    origins="$origins,https://www.$domain"
    
    # Add localhost for development
    origins="$origins,http://localhost:5173"
    origins="$origins,http://localhost:3000"
    origins="$origins,http://127.0.0.1:5173"
    origins="$origins,http://127.0.0.1:3000"
    
    # Remove leading comma
    origins=${origins#,}
    
    echo "$origins"
}

# Main menu
while true; do
    echo -e "${YELLOW}Choose an option:${NC}"
    echo "1) Show current CORS configuration"
    echo "2) Add a domain to CORS origins"
    echo "3) Generate CORS origins for a domain"
    echo "4) Set up CORS for Cloudflare deployment"
    echo "5) Set up CORS for Let's Encrypt deployment"
    echo "6) Set up CORS for development"
    echo "7) Set up CORS for subdomain deployment (frontend + api subdomain)"
    echo "8) Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            echo ""
            show_cors_config
            echo ""
            ;;
        2)
            echo ""
            read -p "Enter domain (e.g., example.com): " domain
            if [ -n "$domain" ]; then
                add_domain_to_cors "$domain"
            else
                echo -e "${RED}Domain cannot be empty${NC}"
            fi
            echo ""
            ;;
        3)
            echo ""
            read -p "Enter domain (e.g., example.com): " domain
            if [ -n "$domain" ]; then
                echo -e "${GREEN}Generated CORS origins for $domain:${NC}"
                echo ""
                generate_cors_origins "$domain"
                echo ""
            else
                echo -e "${RED}Domain cannot be empty${NC}"
            fi
            echo ""
            ;;
        4)
            echo ""
            echo -e "${YELLOW}Setting up CORS for Cloudflare deployment...${NC}"
            read -p "Enter your domain (e.g., guildroster.io): " domain
            if [ -n "$domain" ]; then
                origins=$(generate_cors_origins "$domain")
                add_domain_to_cors "$origins"
                echo -e "${GREEN}✓ CORS configured for Cloudflare deployment${NC}"
                echo -e "${BLUE}Remember to:${NC}"
                echo "  - Add your domain to Cloudflare"
                echo "  - Set DNS records with orange cloud (proxied)"
                echo "  - Configure SSL/TLS to 'Full'"
            else
                echo -e "${RED}Domain cannot be empty${NC}"
            fi
            echo ""
            ;;
        5)
            echo ""
            echo -e "${YELLOW}Setting up CORS for Let's Encrypt deployment...${NC}"
            read -p "Enter your domain (e.g., guildroster.io): " domain
            if [ -n "$domain" ]; then
                origins=$(generate_cors_origins "$domain")
                add_domain_to_cors "$origins"
                echo -e "${GREEN}✓ CORS configured for Let's Encrypt deployment${NC}"
                echo -e "${BLUE}Remember to:${NC}"
                echo "  - Set DNS records with gray cloud (DNS only)"
                echo "  - Run: ./scripts/setup-letsencrypt.sh $domain your-email@example.com"
            else
                echo -e "${RED}Domain cannot be empty${NC}"
            fi
            echo ""
            ;;
        6)
            echo ""
            echo -e "${YELLOW}Setting up CORS for development...${NC}"
            add_domain_to_cors "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
            echo -e "${GREEN}✓ CORS configured for development${NC}"
            echo ""
            ;;
        7)
            echo ""
            echo -e "${YELLOW}Setting up CORS for subdomain deployment...${NC}"
            read -p "Enter your main domain (e.g., guildroster.io): " domain
            if [ -n "$domain" ]; then
                # Generate origins for both main domain and api subdomain
                main_origins=$(generate_cors_origins "$domain")
                api_origins=$(generate_cors_origins "api.$domain")
                all_origins="$main_origins,$api_origins"
                add_domain_to_cors "$all_origins"
                echo -e "${GREEN}✓ CORS configured for subdomain deployment${NC}"
                echo -e "${BLUE}Frontend: $domain${NC}"
                echo -e "${BLUE}Backend API: api.$domain${NC}"
                echo -e "${BLUE}Remember to:${NC}"
                echo "  - Add your domain to Cloudflare"
                echo "  - Set DNS records with orange cloud (proxied)"
                echo "  - Add A record for 'api' subdomain"
                echo "  - Configure SSL/TLS to 'Full'"
            else
                echo -e "${RED}Domain cannot be empty${NC}"
            fi
            echo ""
            ;;
        8)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please enter a number between 1 and 8.${NC}"
            echo ""
            ;;
    esac
done 