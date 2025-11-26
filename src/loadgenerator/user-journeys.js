// User journey definitions matching the original Locust behavior
const { chromium } = require('playwright');
const logger = require('./logger');

const FRONTEND_URL = process.env.FRONTEND_ADDR 
  ? `http://${process.env.FRONTEND_ADDR}` 
  : 'http://frontend:8088';

const products = [
  '0PUK6V6EV0',
  '1YMWWN1N4O',
  '2ZYFJ3GM2N',
  '66VCHSJNUP',
  '6E92ZMYYFZ',
  '9SIQT8TOJO',
  'L9ECAV7KIM',
  'LS4PSXUNUM',
  'OLJCESPC7Z'
];

const currencies = ['EUR', 'USD', 'JPY', 'CAD'];

const randomChoice = (array) => array[Math.floor(Math.random() * array.length)];
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Journey 1: Browser - Just browsing products (most common)
async function browserJourney(page, userId) {
  console.log(`[User ${userId}] Starting browser journey`);
  
  try {
    // Visit homepage
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(randomInt(1000, 3000));
    
    // Browse several products
    const numProducts = randomInt(3, 8);
    for (let i = 0; i < numProducts; i++) {
      const product = randomChoice(products);
      await page.goto(`${FRONTEND_URL}/product/${product}`, { waitUntil: 'networkidle', timeout: 30000 });
      await sleep(randomInt(2000, 5000));
    }
    
    // Maybe change currency
    if (Math.random() > 0.5) {
      const currency = randomChoice(currencies);
      await page.selectOption('select[name="currency_code"]', currency);
      await sleep(randomInt(500, 1500));
    }
    
    console.log(`[User ${userId}] Completed browser journey`);
  } catch (error) {
    console.error(`[User ${userId}] Browser journey error:`, error.message);
  }
}

// Journey 2: Window Shopper - Browse and add to cart but don't checkout
async function windowShopperJourney(page, userId) {
  console.log(`[User ${userId}] Starting window shopper journey`);
  
  try {
    // Visit homepage
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(randomInt(1000, 2000));
    
    // Browse and add items to cart
    const numItems = randomInt(1, 3);
    for (let i = 0; i < numItems; i++) {
      const product = randomChoice(products);
      await page.goto(`${FRONTEND_URL}/product/${product}`, { waitUntil: 'networkidle', timeout: 30000 });
      await sleep(randomInt(1000, 2000));
      
      // Add to cart
      const quantity = randomChoice([1, 2, 3, 4, 5, 10]);
      await page.selectOption('select[name="quantity"]', quantity.toString());
      await page.click('button[type="submit"]:has-text("Add to Cart")');
      await sleep(randomInt(1000, 2000));
    }
    
    // View cart
    await page.goto(`${FRONTEND_URL}/cart`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(randomInt(2000, 4000));
    
    console.log(`[User ${userId}] Completed window shopper journey`);
  } catch (error) {
    console.error(`[User ${userId}] Window shopper journey error:`, error.message);
  }
}

// Journey 3: Buyer - Complete purchase flow
async function buyerJourney(page, userId) {
  logger.info('Starting buyer journey', { user_id: userId, journey_type: 'buyer' });
  
  try {
    // Visit homepage
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(randomInt(1000, 2000));
    
    // Browse a product
    const product = randomChoice(products);
    await page.goto(`${FRONTEND_URL}/product/${product}`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(randomInt(1500, 2500));
    
    // Add to cart
    const quantity = randomChoice([1, 2, 3]);
    await page.selectOption('select[name="quantity"]', quantity.toString());
    await page.click('button[type="submit"]:has-text("Add to Cart")');
    await sleep(randomInt(1000, 2000));
    
    // View cart
    await page.goto(`${FRONTEND_URL}/cart`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(randomInt(1500, 2500));
    
    // Fill checkout form - alternate between two profiles
    const useJason = randomInt(1, 10) >= 7;
    const email = useJason ? 'jason@sudeikis.com' : 'someone@example.com';
    
    // Get current year for expiration (form has current year + 4 years)
    const currentYear = new Date().getFullYear();
    const expirationYear = (currentYear + randomInt(1, 4)).toString();
    
    if (useJason) {
      await page.fill('input[name="email"]', 'jason@sudeikis.com');
      await page.fill('input[name="street_address"]', '742 Evergreen Terrace');
      await page.fill('input[name="zip_code"]', '90210');
      await page.fill('input[name="city"]', 'Beverly Hills');
      await page.fill('input[name="state"]', 'CA');
      await page.fill('input[name="country"]', 'United States');
      await page.fill('input[name="credit_card_number"]', '4111-1111-1111-1111');
      await page.selectOption('select[name="credit_card_expiration_month"]', '12');
      await page.selectOption('select[name="credit_card_expiration_year"]', expirationYear);
      await page.fill('input[name="credit_card_cvv"]', '123');
    } else {
      await page.fill('input[name="email"]', 'someone@example.com');
      await page.fill('input[name="street_address"]', '1600 Amphitheatre Parkway');
      await page.fill('input[name="zip_code"]', '94043');
      await page.fill('input[name="city"]', 'Mountain View');
      await page.fill('input[name="state"]', 'CA');
      await page.fill('input[name="country"]', 'United States');
      await page.fill('input[name="credit_card_number"]', '4432-8015-6152-0454');
      await page.selectOption('select[name="credit_card_expiration_month"]', '1');
      await page.selectOption('select[name="credit_card_expiration_year"]', expirationYear);
      await page.fill('input[name="credit_card_cvv"]', '672');
    }
    
    await sleep(randomInt(500, 1000));
    
    // Complete order (Place Order button)
    await page.click('button[type="submit"]:has-text("Place Order")');
    await page.waitForLoadState('networkidle', { timeout: 45000 });
    await sleep(randomInt(2000, 4000));
    
    logger.info('Completed buyer journey - Order placed', { 
      user_id: userId, 
      journey_type: 'buyer', 
      product_id: product,
      customer_email: email,
      quantity: quantity
    });
  } catch (error) {
    logger.error('Buyer journey error', { user_id: userId, journey_type: 'buyer', error: error.message });
  }
}

// Journey 4: Currency Changer - Focus on currency changes
async function currencyChangerJourney(page, userId) {
  logger.info('Starting currency changer journey', { user_id: userId, journey_type: 'currency_changer' });
  
  try {
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(randomInt(1000, 2000));
    
    // Try different currencies
    const numChanges = randomInt(2, 4);
    for (let i = 0; i < numChanges; i++) {
      const currency = randomChoice(currencies);
      await page.selectOption('select[name="currency_code"]', currency);
      await sleep(randomInt(1000, 2000));
      
      // Browse a product in that currency
      const product = randomChoice(products);
      await page.goto(`${FRONTEND_URL}/product/${product}`, { waitUntil: 'networkidle', timeout: 30000 });
      await sleep(randomInt(1500, 2500));
    }
    
    logger.info('Completed currency changer journey', { user_id: userId, journey_type: 'currency_changer', currency_changes: numChanges });
  } catch (error) {
    logger.error('Currency changer journey error', { user_id: userId, journey_type: 'currency_changer', error: error.message });
  }
}

// Select journey based on weighted probabilities (matching Locust weights)
// Original weights: {index: 1, setCurrency: 2, browseProduct: 10, addToCart: 2, viewCart: 3, checkout: 1}
// Translated to journeys:
// - browserJourney: 55% (most common - browsing)
// - windowShopperJourney: 25% (adds to cart, views cart)
// - buyerJourney: 10% (completes checkout)
// - currencyChangerJourney: 10% (currency focused)
function selectJourney() {
  const rand = Math.random() * 100;
  
  if (rand < 55) return browserJourney;
  if (rand < 80) return windowShopperJourney;
  if (rand < 90) return buyerJourney;
  return currencyChangerJourney;
}

// Run a continuous user session
async function runUserSession(userId) {
  let browser;
  
  try {
    // Launch browser with realistic viewport
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });
    
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    
    // Run journeys continuously
    while (true) {
      const journey = selectJourney();
      await journey(page, userId);
      
      // Wait between journeys (1-10 seconds, matching Locust's wait_time)
      const waitTime = randomInt(1000, 10000);
      logger.debug('Waiting before next journey', { user_id: userId, wait_ms: waitTime });
      await sleep(waitTime);
    }
  } catch (error) {
    logger.error('User session error', { user_id: userId, error: error.message, stack: error.stack });
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

module.exports = {
  runUserSession
};

