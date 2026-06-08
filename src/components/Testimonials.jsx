const items = [
  {
    quote: "LucidSight caught an intruder in my warehouse at 3AM and alerted me immediately. The police arrived before they could steal anything.",
    name: "Michael Rodriguez", role: "Small Business Owner",
    img: "https://randomuser.me/api/portraits/men/32.jpg", stars: 5,
  },
  {
    quote: "As a security professional, I'm impressed with the accuracy of the human detection. Fewer false alarms than expensive commercial systems.",
    name: "Sarah Chen", role: "Security Consultant",
    img: "https://randomuser.me/api/portraits/women/44.jpg", stars: 5,
  },
  {
    quote: "The peace of mind is worth every penny. I travel frequently and can check on my home anytime with LucidSight monitoring.",
    name: "David Wilson", role: "Frequent Traveler",
    img: "https://randomuser.me/api/portraits/men/75.jpg", stars: 4.5,
  },
];

function Stars({ count }) {
  const full = Math.floor(count);
  const half = count % 1 !== 0;
  return (
    <div className="text-yellow-400 mr-2">
      {Array.from({ length: full }).map((_, i) => <i key={i} className="fas fa-star"></i>)}
      {half && <i className="fas fa-star-half-alt"></i>}
    </div>
  );
}

export default function Testimonials() {
  return (
    <section className="py-16 px-4 md:px-8 bg-indigo-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Trusted by Security Professionals</h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">What our customers say about LucidSight</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {items.map((t) => (
            <div key={t.name} className="bg-white p-8 rounded-xl shadow-sm">
              <div className="flex items-center mb-4"><Stars count={t.stars} /></div>
              <p className="text-slate-600 mb-6">"{t.quote}"</p>
              <div className="flex items-center">
                <img src={t.img} alt={t.name} className="w-10 h-10 rounded-full mr-3" />
                <div>
                  <h4 className="font-bold">{t.name}</h4>
                  <p className="text-sm text-slate-500">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
