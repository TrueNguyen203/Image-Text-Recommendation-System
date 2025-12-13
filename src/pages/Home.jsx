import Product from '../components/Product';


export default function Home() {
  const products = [
    {
      name: 'New Look trench coat in camel',
      size: 'UK 4,UK 6,UK 8,UK 10,UK 12,UK 14',
      brand: 'New Look',
      price: 158.00,
      color: 'Newtral',
      sku: 1,
      description: [{'Product Details': 'Coats & Jackets by New LookLow-key layeringNotch collarButton placketTie waistRegular fitProduct Code: 126704571'}, {'Brand': 'Since setting up shop in the 60s, New Look has become a high-street classic known for creating universally loved, wardrobe-ready collections. Shop the New Look at ASOS edit, featuring everything from chic LBDs and printed dresses to all-important accessories and figure-flattering jeans (if you re anything like us, you re always on the hunt for those). While you re there, check out the label s cute-yet-classy tops and blouses for your next jeans and a nice top day.'}, {'Size & Fit': "Model wears: UK 8/ EU 36/ US 4Model's height: 170 cm/5'7 "}, {'Look After Me': 'Machine wash according to instructions on care label'}, {'About Me': 'Stretch, plain-woven fabricMain: 55% Polyester, 45% Elastomultiester.'}],
      images: ['https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-4?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-1-neutral?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-2?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-3?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-4?$n_1920w$&wid=1926&fit=constrain'],
    },
    {
      name: 'JDY oversized trench coat in stone',
      size: 'UK 4,UK 6,UK 8,UK 10,UK 12,UK 14',
      brand: 'JDY',
      price: 139.12,
      color: 'STONE',
      sku: 2,
      description: [{'Product Details': 'Coats & Jackets by JDYLow-key layeringNotch collarButton placketBelted waistSide pocketsOversized fitProduct Code: 125806824'}, {'Brand': 'JDY collection here at ASOS is a bit of us, and we think it ll be a bit of you, too. Mix and match its dreamy denim skirts and jeans with trusty jersey pieces, or snap up an entire look in a striped or polka-dot co-ord. Its ditsy-print dresses are just the right amount of kitsch, too.'}, {'Size & Fit': 'Model\'s height: 167.5cm/5\'6"Model is wearing: UK S/ EU S/ US XS'}, {'Look After Me': 'Machine wash according to instructions on care label'}, {'About Me': 'Plain-woven fabricMain: 90% Polyester, 10% Nylon.'}],
      images: ['https://images.asos-media.com/products/jdy-oversized-trench-coat-in-stone/204198578-4?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/jdy-oversized-trench-coat-in-stone/204198578-1-stone?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/jdy-oversized-trench-coat-in-stone/204198578-2?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/jdy-oversized-trench-coat-in-stone/204198578-3?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/jdy-oversized-trench-coat-in-stone/204198578-4?$n_1920w$&wid=1926&fit=constrain'],
    },
    {
      name: 'Stradivarius double breasted wool coat in grey',
      size: 'UK 4,UK 6,UK 8,UK 10,UK 12,UK 14',
      brand: 'Stradivarius',
      price: 59.99,
      color: 'GREY',
      sku: 3,
      description: [{'Product Details': 'Coats & Jackets by StradivariusJacket upgrade: checkNotch collarSingle-button fasteningSide pocketsRegular fitProduct Code: 123650194'}, {'Brand': 'Barcelona-born clothing brand Stradivarius moves to its own beat. With an eye for minimalism and trend-led detail, expect classic silhouettes and a neutral colour palette (with the odd print thrown in for good measure). The perfect stop for a wardrobe refresh, our Stradivarius at ASOS edit has everything from floaty day dresses and blouses to staple jeans and T-shirts. Looking for layers? Check out the brand s jumpers, jackets and blazers.'}, {'Size & Fit': 'Model wears: UK S/ EU S/ US XSModel\'s height: 168cm/5\'6"'}, {'Look After Me': 'Machine wash according to instructions on care label'}, {'About Me': 'Wool-mix fabricLining: 100% Polyester, Main: 53% Polyester, 30% Wool, 9% Acrylic, 8% Other fibres.'}],
      images: ['https://images.asos-media.com/products/stradivarius-double-breasted-wool-coat-in-grey/203958042-4?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/stradivarius-double-breasted-wool-coat-in-grey/203958042-1-grey?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/stradivarius-double-breasted-wool-coat-in-grey/203958042-2?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/stradivarius-double-breasted-wool-coat-in-grey/203958042-3?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/stradivarius-double-breasted-wool-coat-in-grey/203958042-4?$n_1920w$&wid=1926&fit=constrain'],
    },
    {
      name: 'ASOS DESIGN denim bomber in ecru',
      size: 'UK 4,UK 6,UK 8,UK 10,UK 12,UK 14',
      brand: 'ASOS DESIGN',
      price: 200.00,
      color: 'ECRU',
      sku: 4,
      description: [{'Product Details': 'Coats & Jackets by ASOS DESIGNThe denim of your dreamsBaseball collarZip fasteningSide pocketsOversized fitProduct Code: 127124035'}, {'Brand': 'This is ASOS DESIGN your go-to for all the latest trends, no matter who you are, where you re from and what you re up to. Exclusive to ASOS, our universal brand is here for you, and comes in all our fit ranges: ASOS Curve, Tall, Petite and Maternity. Created by us, styled by you.'}, {'Size & Fit': "Model's height: 178cm / 5' 10''Model is wearing: UK 8/ EU 36/ US 4"}, {'Look After Me': 'Machine wash according to instructions on care label'}, {'About Me': 'Non-stretch denim: ecru washMain: 100% Cotton.'}],
      images: ['https://images.asos-media.com/products/asos-design-denim-bomber-in-ecru/204408584-5?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/asos-design-denim-bomber-in-ecru/204408584-1-ecru?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/asos-design-denim-bomber-in-ecru/204408584-2?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/asos-design-denim-bomber-in-ecru/204408584-3?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/asos-design-denim-bomber-in-ecru/204408584-4?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/asos-design-denim-bomber-in-ecru/204408584-5?$n_1920w$&wid=1926&fit=constrain'],
    },
  ];

  return (
    <div className="bg-white mt-20">
      {/* Products Grid */}
      <div className="px-6 py-12 max-w-8xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {products.map((product) =>
            <Product key={product.sku} {...product} />
          )}
          {products.map((product) =>
            <Product key={product.sku} {...product} />
          )}
          {products.map((product) =>
            <Product key={product.sku} {...product} />
          )}
        </div>
      </div>
    </div>
  );
}