export default function Footer() {
  return (
    <footer id="contact" className="bg-slate-900 text-grey py-12 px-4 md:px-8">
      <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
        <div>
          <div className="flex items-center mb-4">
            <i className="fas fa-eye text-2xl text-indigo-400 mr-2"></i>
            <span className="text-xl font-bold text-white">LucidSight</span>
          </div>
          <p className="text-slate-400">Advanced AI surveillance for home and business security.</p>
        </div>
        <div>
          <h4 className="font-bold text-lg mb-4 text-white">Product</h4>
          <ul className="space-y-2">
            <li><a href="#features" className="text-slate-400 hover:text-white transition-colors">Features</a></li>
            <li><a href="#how-it-works" className="text-slate-400 hover:text-white transition-colors">How It Works</a></li>
            <li><a href="#contact" className="text-slate-400 hover:text-white transition-colors">Contact</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-lg mb-4 text-white">Connect</h4>
          <div className="flex space-x-4">
            <a href="#" className="text-slate-400 hover:text-white text-xl"><i className="fab fa-twitter"></i></a>
            <a href="#" className="text-slate-400 hover:text-white text-xl"><i className="fab fa-facebook"></i></a>
            <a href="#" className="text-slate-400 hover:text-white text-xl"><i className="fab fa-linkedin"></i></a>
            <a href="#" className="text-slate-400 hover:text-white text-xl"><i className="fab fa-github"></i></a>
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto pt-8 mt-8 border-t border-slate-800 text-center text-slate-400 text-sm">
        <p>© 2023 LucidSight Technologies. All rights reserved.</p>
      </div>
    </footer>
  );
}
