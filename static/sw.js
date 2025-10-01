// Service Worker para PWA - Compatível com iPad Air 1 (iOS 7-12)
const CACHE_NAME = 'midnight-pdv-v1.0.0';
const OFFLINE_PAGE = '/offline';

// Recursos essenciais para cache
const ESSENTIAL_RESOURCES = [
  '/pdv-full',
  '/static/manifest.json',
  // Adicionar outros recursos críticos conforme necessário
];

// Recursos que podem ser cached dinamicamente
const DYNAMIC_CACHE_RESOURCES = [
  '/api/produtos',
  '/api/usuarios/current',
];

// Instalação do Service Worker
self.addEventListener('install', function(event) {
  console.log('🔧 Service Worker: Instalando...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('📦 Service Worker: Cache aberto');
        return cache.addAll(ESSENTIAL_RESOURCES);
      })
      .then(function() {
        console.log('✅ Service Worker: Recursos essenciais cacheados');
        return self.skipWaiting();
      })
      .catch(function(error) {
        console.error('❌ Service Worker: Erro na instalação:', error);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', function(event) {
  console.log('🚀 Service Worker: Ativando...');
  
  event.waitUntil(
    caches.keys()
      .then(function(cacheNames) {
        return Promise.all(
          cacheNames.map(function(cacheName) {
            if (cacheName !== CACHE_NAME) {
              console.log('🗑️ Service Worker: Removendo cache antigo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(function() {
        console.log('✅ Service Worker: Ativado');
        return self.clients.claim();
      })
  );
});

// Interceptação de requisições
self.addEventListener('fetch', function(event) {
  // Ignorar requisições não-GET
  if (event.request.method !== 'GET') {
    return;
  }

  // Ignorar requisições para domínios externos
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Se encontrou no cache, retorna
        if (response) {
          console.log('📋 Cache hit:', event.request.url);
          return response;
        }

        // Se não encontrou no cache, busca na rede
        return fetch(event.request)
          .then(function(response) {
            // Se não conseguiu buscar na rede
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clona a resposta para cachear
            var responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then(function(cache) {
                // Cache apenas recursos específicos dinamicamente
                if (shouldCacheDynamically(event.request.url)) {
                  console.log('💾 Cacheando dinamicamente:', event.request.url);
                  cache.put(event.request, responseToCache);
                }
              });

            return response;
          })
          .catch(function() {
            // Se está offline e é uma página HTML, mostrar página offline
            if (event.request.destination === 'document') {
              return caches.match(OFFLINE_PAGE);
            }
            
            // Para outros recursos, retorna resposta vazia ou padrão
            return new Response('', {
              status: 408,
              statusText: 'Request timeout - Offline'
            });
          });
      })
  );
});

// Função para determinar se deve cachear dinamicamente
function shouldCacheDynamically(url) {
  return DYNAMIC_CACHE_RESOURCES.some(function(resource) {
    return url.includes(resource);
  });
}

// Listener para mensagens do cliente (para atualizações)
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('🔄 Service Worker: Aplicando atualização...');
    self.skipWaiting();
  }
});

// Sincronização em background (para quando voltar online)
self.addEventListener('sync', function(event) {
  if (event.tag === 'background-sync') {
    console.log('🔄 Service Worker: Sincronização em background');
    // Implementar lógica de sincronização quando necessário
  }
});