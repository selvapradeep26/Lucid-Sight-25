export default function Navbar() {
  return (
    <nav className="navbar fixed w-full z-50 py-3 px-4 md:px-8">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center">
          <i className="fas fa-eye text-2xl text-indigo-600 mr-2"></i>
          <span className="text-xl font-bold text-slate-800">LucidSight</span>
        </div>
        <div className="hidden md:flex space-x-20">
          <a href="#features" className="text-slate-600 hover:text-indigo-600 font-medium">Features</a>
          <a href="#how-it-works" className="text-slate-600 hover:text-indigo-600 font-medium">How It Works</a>
          <a href="#contact" className="text-slate-600 hover:text-indigo-600 font-medium">Contact</a>
        </div>
        <div className="flex items-center space-x-4">
          <a href="#demo" className="hidden md:block btn-secondary px-4 py-2 rounded-lg font-medium">Live Demo</a>
          <a href="#detection" className="btn-primary px-4 py-2 rounded-lg font-medium text-white">Get Started</a>
        </div>
      </div>
    </nav>
  );
}
