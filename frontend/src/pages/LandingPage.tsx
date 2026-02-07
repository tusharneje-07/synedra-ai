import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Brain, ShieldCheck, TrendingUp, Eye, MessageSquare, Zap, ArrowRight } from "lucide-react";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-[#0B1220] text-[#E2E8F0]">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 border-b border-white/5 bg-[#0B1220]/80 backdrop-blur-md">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-xl font-bold">
                MarkitAI
              </Link>
              <div className="hidden md:flex items-center gap-6">
                <a href="#product" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                  Product
                </a>
                <a href="#how-it-works" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                  How It Works
                </a>
                <a href="#pricing" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                  Pricing
                </a>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login">
                <Button variant="ghost" className="text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-white/5">
                  Login
                </Button>
              </Link>
              <Link to="/register">
                <Button className="bg-[#3B82F6] hover:bg-[#3B82F6]/90 text-white">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 md:py-32">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Autonomous AI Marketing Council
            </h1>
            <p className="text-xl text-[#94A3B8] mb-8 leading-relaxed">
              Multiple AI agents debate, decide, and optimize your social strategy automatically.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/register">
                <Button size="lg" className="bg-[#3B82F6] hover:bg-[#3B82F6]/90 text-white">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/dashboard">
                <Button size="lg" variant="outline" className="border-[#3B82F6]/30 text-[#E2E8F0] hover:bg-[#3B82F6]/10">
                  View Demo
                </Button>
              </Link>
            </div>
          </div>
          
          <div className="relative">
            <div className="relative rounded-xl overflow-hidden bg-gradient-to-br from-[#3B82F6]/20 to-[#0F172A] p-8 shadow-2xl border border-white/5">
              {/* Mockup preview */}
              <div className="aspect-video bg-[#0F172A] rounded-lg border border-white/10 flex items-center justify-center">
                <div className="text-center p-8">
                  <Brain className="h-16 w-16 text-[#3B82F6] mx-auto mb-4" />
                  <p className="text-sm text-[#94A3B8]">AI Council Dashboard</p>
                </div>
              </div>
              {/* Glow effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-[#3B82F6]/10 to-purple-500/10 blur-3xl -z-10" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="product" className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Powered by Multi-Agent Intelligence
          </h2>
          <p className="text-lg text-[#94A3B8] max-w-2xl mx-auto">
            AI agents that work together to create, review, and optimize your marketing strategy.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Feature 1 */}
          <div className="group bg-[#0F172A] rounded-xl p-6 border border-white/5 hover:border-[#3B82F6]/30 transition-all hover:shadow-lg hover:shadow-[#3B82F6]/5">
            <div className="h-12 w-12 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center mb-4 group-hover:bg-[#3B82F6]/20 transition-colors">
              <MessageSquare className="h-6 w-6 text-[#3B82F6]" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Multi-Agent Debate Engine</h3>
            <p className="text-sm text-[#94A3B8] leading-relaxed">
              Agents discuss, challenge, and refine ideas before execution.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="group bg-[#0F172A] rounded-xl p-6 border border-white/5 hover:border-[#3B82F6]/30 transition-all hover:shadow-lg hover:shadow-[#3B82F6]/5">
            <div className="h-12 w-12 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center mb-4 group-hover:bg-[#3B82F6]/20 transition-colors">
              <ShieldCheck className="h-6 w-6 text-[#3B82F6]" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Risk & Brand Governance</h3>
            <p className="text-sm text-[#94A3B8] leading-relaxed">
              Built-in compliance checks and brand safety protocols.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="group bg-[#0F172A] rounded-xl p-6 border border-white/5 hover:border-[#3B82F6]/30 transition-all hover:shadow-lg hover:shadow-[#3B82F6]/5">
            <div className="h-12 w-12 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center mb-4 group-hover:bg-[#3B82F6]/20 transition-colors">
              <TrendingUp className="h-6 w-6 text-[#3B82F6]" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Closed-Loop Learning</h3>
            <p className="text-sm text-[#94A3B8] leading-relaxed">
              Agents learn from each campaign and improve over time.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="group bg-[#0F172A] rounded-xl p-6 border border-white/5 hover:border-[#3B82F6]/30 transition-all hover:shadow-lg hover:shadow-[#3B82F6]/5">
            <div className="h-12 w-12 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center mb-4 group-hover:bg-[#3B82F6]/20 transition-colors">
              <Eye className="h-6 w-6 text-[#3B82F6]" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Strategy Transparency</h3>
            <p className="text-sm text-[#94A3B8] leading-relaxed">
              Full visibility into every decision the council makes.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            How It Works
          </h2>
          <p className="text-lg text-[#94A3B8]">
            Three simple steps to autonomous marketing
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {/* Step 1 */}
          <div className="text-center">
            <div className="h-16 w-16 rounded-xl bg-[#3B82F6]/10 flex items-center justify-center mx-auto mb-4 border border-[#3B82F6]/20">
              <Eye className="h-8 w-8 text-[#3B82F6]" />
            </div>
            <h3 className="text-xl font-semibold mb-3">1. Observe</h3>
            <p className="text-[#94A3B8]">
              Agents monitor trends, competitors, and audience sentiment in real-time.
            </p>
          </div>

          {/* Step 2 */}
          <div className="text-center">
            <div className="h-16 w-16 rounded-xl bg-[#3B82F6]/10 flex items-center justify-center mx-auto mb-4 border border-[#3B82F6]/20">
              <MessageSquare className="h-8 w-8 text-[#3B82F6]" />
            </div>
            <h3 className="text-xl font-semibold mb-3">2. Debate</h3>
            <p className="text-[#94A3B8]">
              Council members challenge each idea through structured debate until consensus.
            </p>
          </div>

          {/* Step 3 */}
          <div className="text-center">
            <div className="h-16 w-16 rounded-xl bg-[#3B82F6]/10 flex items-center justify-center mx-auto mb-4 border border-[#3B82F6]/20">
              <Zap className="h-8 w-8 text-[#3B82F6]" />
            </div>
            <h3 className="text-xl font-semibold mb-3">3. Act & Learn</h3>
            <p className="text-[#94A3B8]">
              Execute approved strategies and continuously improve from results.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="bg-gradient-to-br from-[#3B82F6]/10 to-purple-500/10 rounded-2xl p-12 md:p-16 text-center border border-[#3B82F6]/20">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to replace your marketing team with AI agents?
          </h2>
          <p className="text-lg text-[#94A3B8] mb-8 max-w-2xl mx-auto">
            Join forward-thinking companies using autonomous AI to scale their marketing.
          </p>
          <Link to="/register">
            <Button size="lg" className="bg-[#3B82F6] hover:bg-[#3B82F6]/90 text-white text-lg px-8">
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 mt-20">
        <div className="container mx-auto px-6 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="font-bold text-lg mb-4">MarkitAI</h3>
              <p className="text-sm text-[#94A3B8]">
                Autonomous AI Marketing Council
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    Security
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    Careers
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    Privacy
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors">
                    Terms
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-white/5 text-center text-sm text-[#94A3B8]">
            © 2026 MarkitAI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
