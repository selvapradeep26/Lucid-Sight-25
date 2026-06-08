export default function Hero() {
  return (
    <section className="hero-gradient text-white pt-32 pb-20 px-4 md:px-8">
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
            AI-Powered Human Detection for Your Security
          </h1>
          <p className="text-xl text-indigo-100 mb-8">
            Real-time intruder alerts delivered instantly to your phone or email. Sleep soundly knowing LucidSight is watching.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <a href="#detection" className="btn-secondary px-6 py-3 rounded-lg font-medium text-center">Start Detection Now</a>
            <a href="#how-it-works" className="bg-white/10 hover:bg-white/20 px-6 py-3 rounded-lg font-medium text-center border border-white/20 transition-all">Learn More</a>
          </div>
        </div>
        <div className="relative">
          <img
            src="https://150085848.v2.pressablecdn.com/wp-content/uploads/2024/03/0324-March-Headers_Feature1-AISmartHome-Thumbnail.jpg"
            alt="Security monitoring"
            className="rounded-xl shadow-2xl border-4 border-white/20"
          />
          <div className="absolute -bottom-6 -right-6 bg-white p-4 rounded-xl shadow-lg">
            <div className="flex items-center">
              <div className="status-indicator status-active mr-2"></div>
              <span className="font-medium text-gray-500">Live Detection</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
