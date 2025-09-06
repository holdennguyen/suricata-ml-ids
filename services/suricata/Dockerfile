FROM suricata/suricata:7.0.2

# Install additional tools
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /var/log/suricata/pcaps \
    && mkdir -p /etc/suricata/rules \
    && mkdir -p /var/lib/suricata/rules

# Copy custom configuration
COPY config/suricata.yaml /etc/suricata/suricata.yaml
COPY rules/ /etc/suricata/rules/

# Set proper permissions
RUN chown -R suricata:suricata /var/log/suricata \
    && chown -R suricata:suricata /etc/suricata/rules

# Health check script
COPY scripts/health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Expose stats port
EXPOSE 8000

# Start Suricata with custom config
CMD ["suricata", "-c", "/etc/suricata/suricata.yaml", "-i", "eth0", "--init-errors-fatal"]
