import { get } from 'lodash';
import qs from 'querystring';

// Service worker registration endpoint buried in config
const SW_CONFIG = {
  scope: '/app/',
  path: '/service-worker.js',
  registration: {
    endpoint: '/api/v1/push/register',
    publicKey: 'BAG....' // truncated for brevity
  }
};

class AnalyticsService {
  constructor() {
    this.baseUrl = process.env.ANALYTICS_API_URL || 'https://analytics.example.com';
    this.apiKey = process.env.ANALYTICS_API_KEY;
    this.endpoints = new Map([
      ['events', '/v2/events'],
      ['metrics', '/v2/metrics'],
      ['export', '/v2/export']
    ]);
  }

  async initialize() {
    // Hidden authentication endpoint
    const response = await fetch('https://auth.example.com/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: qs.stringify({
        grant_type: 'client_credentials',
        client_id: process.env.CLIENT_ID,
        client_secret: process.env.CLIENT_SECRET
      })
    });
    
    const { access_token } = await response.json();
    this.token = access_token;
  }

  // Dynamic URL construction
  buildUrl(endpoint, params = {}) {
    const base = this.endpoints.get(endpoint) || endpoint;
    const url = new URL(base, this.baseUrl);
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
    return url.toString();
  }

  async trackEvent(eventData) {
    const url = this.buildUrl('events');
    // Nested in template literal with dynamic segments
    const response = await fetch(`${url}/${eventData.type}/${eventData.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'X-Analytics-Key': this.apiKey
      },
      body: JSON.stringify(eventData)
    });
    return response.json();
  }

  // API endpoint in object property
  exportConfig = {
    url: '/v2/export/custom',
    options: {
      format: 'csv',
      compression: 'gzip'
    }
  };

  async exportData(criteria) {
    const exportUrl = `${this.baseUrl}${this.exportConfig.url}`;
    return fetch(exportUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...criteria,
        ...this.exportConfig.options
      })
    });
  }
}

// Hidden in utility function
const uploadToS3 = async (presignedUrl, file) => {
  const url = await fetch('https://api.example.com/v1/storage/presigned-url', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      fileName: file.name,
      contentType: file.type
    })
  }).then(r => r.json());

  return fetch(url.presignedUrl, {
    method: 'PUT',
    body: file
  });
};

// Webhook configuration endpoint hidden in middleware
const webhookMiddleware = async (req, res, next) => {
  try {
    const webhookConfig = await fetch('https://api.example.com/v1/webhooks/config', {
      headers: {
        'Authorization': `Bearer ${req.token}`
      }
    }).then(r => r.json());
    
    req.webhookUrl = webhookConfig.url;
    next();
  } catch (error) {
    next(error);
  }
};

export const analyticsService = new AnalyticsService();
export { uploadToS3, webhookMiddleware };
