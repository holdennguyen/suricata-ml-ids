FROM jasonish/suricata:7.0.2

# Create necessary directories
RUN mkdir -p /var/log/suricata/pcaps \
    && mkdir -p /etc/suricata/rules \
    && mkdir -p /var/lib/suricata/rules

# Copy custom configuration with proper permissions
COPY config/suricata.yaml /etc/suricata/suricata.yaml
COPY rules/ /etc/suricata/rules/

# Fix permissions for configuration files
RUN chown -R suricata:suricata /etc/suricata/ \
    && chown -R suricata:suricata /var/log/suricata/ \
    && chown -R suricata:suricata /var/lib/suricata/ \
    && chmod 644 /etc/suricata/suricata.yaml

# Health check script
COPY scripts/health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Expose stats port
EXPOSE 8000

# Start Suricata with custom config
CMD ["suricata", "-c", "/etc/suricata/suricata.yaml", "-i", "eth0", "--init-errors-fatal"]
