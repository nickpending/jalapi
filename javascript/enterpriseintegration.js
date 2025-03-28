import { curry, get, template } from 'lodash';
import axios from 'axios';
import { parse as parseUrl } from 'url';
import { Buffer } from 'buffer';
import WebSocket from 'ws';

// Deep nested configuration with environment overrides
const CONFIG = {
  api: {
    version: 'v3',
    environments: {
      dev: {
        gateway: 'https://dev-gateway.enterprise.com',
        services: {
          auth: '/auth',
          data: '/data-service',
          ml: '/ml-predictions',
          events: '/event-stream'
        }
      },
      prod: {
        gateway: 'https://api.enterprise.com',
        services: {
          auth: '/auth/v3',
          data: '/data/v2',
          ml: '/ml/v1',
          events: '/events'
        }
      }
    },
    defaultHeaders: {
      'X-API-Version': '3.0.0',
      'Accept': 'application/json'
    }
  },
  features: {
    enableWebsocket: true,
    enableSSE: false,
    batchSize: 100
  }
};

// Dynamic endpoint template generator
const createEndpointTemplate = (path, params = {}) => {
  const compiled = template(path, {
    interpolate: /{{([\s\S]+?)}}/g
  });
  return (data) => compiled({ ...params, ...data });
};

// Complex service discovery mechanism
class ServiceRegistry {
  #services = new Map();
  #templates = new WeakMap();
  
  constructor() {
    this.env = process.env.NODE_ENV || 'dev';
    this.baseUrl = CONFIG.api.environments[this.env].gateway;
  }

  register(name, config) {
    const endpoints = new Proxy({}, {
      get: (target, prop) => {
        if (!target[prop]) {
          // Dynamically generate endpoint URL
          const servicePath = CONFIG.api.environments[this.env].services[name];
          target[prop] = `${this.baseUrl}${servicePath}${config.endpoints[prop]}`;
        }
        return target[prop];
      }
    });

    this.#services.set(name, {
      ...config,
      endpoints
    });
  }

  getEndpoint(serviceName, endpointName, params = {}) {
    const service = this.#services.get(serviceName);
    if (!service) throw new Error(`Service ${serviceName} not registered`);
    
    let template = this.#templates.get(service.endpoints[endpointName]);
    if (!template) {
      template = createEndpointTemplate(service.endpoints[endpointName]);
      this.#templates.set(service.endpoints[endpointName], template);
    }
    
    return template(params);
  }
}

// Initialize service registry with complex endpoint patterns
const registry = new ServiceRegistry();

registry.register('auth', {
  endpoints: {
    login: '/oauth2/token',
    refresh: '/oauth2/refresh',
    logout: '/oauth2/revoke',
    verify: '/verify-token',
    mfa: '/mfa/challenge'
  }
});

registry.register('users', {
  endpoints: {
    profile: '/users/{{userId}}/profile',
    preferences: '/users/{{userId}}/preferences?locale={{locale}}',
    activity: '/users/{{userId}}/activity/{{type}}/{{period}}',
    reports: '/reports/users/{{userId}}/{{reportType}}'
  }
});

// GraphQL client with dynamic endpoint generation
class GraphQLClient {
  #endpoint;
  
  constructor(endpoint) {
    this.#endpoint = endpoint;
  }

  async query(document, variables = {}) {
    const response = await fetch(`${CONFIG.api.environments[process.env.NODE_ENV || 'dev'].gateway}/graphql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...CONFIG.api.defaultHeaders
      },
      body: JSON.stringify({
        query: document,
        variables
      })
    });
    return response.json();
  }
}

// WebSocket connection manager with reconnection logic
class WebSocketManager {
  constructor() {
    const wsUrl = new URL('/ws', CONFIG.api.environments[process.env.NODE_ENV || 'dev'].gateway);
    wsUrl.protocol = wsUrl.protocol.replace('http', 'ws');
    
    this.ws = new WebSocket(wsUrl.toString());
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    this.ws.on('message', async (data) => {
      const message = JSON.parse(data);
      if (message.type === 'SYNC_REQUIRED') {
        // Hidden API endpoint in message handler
        await fetch(`${CONFIG.api.environments[process.env.NODE_ENV || 'dev'].gateway}/api/v1/sync`, {
          method: 'POST',
          headers: CONFIG.api.defaultHeaders
        });
      }
    });
  }
}

// API client factory with dynamic middleware injection
const createApiClient = (config = {}) => {
  const client = axios.create({
    baseURL: CONFIG.api.environments[process.env.NODE_ENV || 'dev'].gateway,
    headers: CONFIG.api.defaultHeaders,
    ...config
  });

  // Request interceptor with dynamic endpoint resolution
  client.interceptors.request.use(async (config) => {
    // Hidden endpoint in interceptor
    const featureFlags = await fetch('/api/v1/features/flags').then(r => r.json());
    
    if (featureFlags.enableNewEndpoints) {
      config.url = config.url.replace('/v2/', '/v3/');
    }
    
    return config;
  });

  return client;
};

// Nested service definitions with dynamic routing
const services = {
  data: {
    async query(params) {
      const queryBuilder = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        queryBuilder.append(key, value);
      });
      
      // Complex URL construction
      const url = `${CONFIG.api.environments[process.env.NODE_ENV || 'dev'].gateway}${
        CONFIG.api.environments[process.env.NODE_ENV || 'dev'].services.data
      }/query?${queryBuilder.toString()}`;
      
      return fetch(url, {
        headers: CONFIG.api.defaultHeaders
      });
    },
    export: {
      // Nested endpoint in method
      async generateReport(type, format) {
        const response = await fetch(`/api/v2/export/${type}?format=${format}`);
        const { taskId } = await response.json();
        
        // Polling endpoint
        return fetch(`/api/v2/tasks/${taskId}/status`);
      }
    }
  },
  ml: {
    async predict(modelId, data) {
      // Template literal with nested path construction
      const modelEndpoint = `${CONFIG.api.environments[process.env.NODE_ENV || 'dev'].services.ml}/models/${modelId}/predict`;
      return fetch(modelEndpoint, {
        method: 'POST',
        body: JSON.stringify(data)
      });
    }
  }
};

// Dynamic API versioning middleware
const apiVersionMiddleware = curry((version, handler) => async (req, res, next) => {
  // Version-specific endpoint
  const versionInfo = await fetch(`/api/version-info/${version}`);
  const { deprecated, successor } = await versionInfo.json();
  
  if (deprecated) {
    // Migration endpoint
    await fetch(`/api/v1/usage/report-deprecated`, {
      method: 'POST',
      body: JSON.stringify({
        endpoint: req.path,
        version,
        successor
      })
    });
  }
  
  return handler(req, res, next);
});

// Hidden webhook configuration
const webhookService = {
  async configure(config) {
    const response = await fetch('/api/v2/webhooks/register', {
      method: 'POST',
      body: JSON.stringify(config)
    });
    
    const { webhookId } = await response.json();
    
    // Nested endpoint in configuration
    return fetch(`/api/v2/webhooks/${webhookId}/test`, {
      method: 'POST'
    });
  }
};

export {
  registry,
  createApiClient,
  services,
  apiVersionMiddleware,
  webhookService
};
