import { useState } from "react";
import { X, Plus, Save, RotateCcw } from "lucide-react";
import { Link } from "react-router-dom";
import ThemeToggle from "@/components/dashboard/ThemeToggle";

const Settings = () => {
  // Form state
  const [brandName, setBrandName] = useState("");
  const [brandTone, setBrandTone] = useState("Professional");
  const [brandDescription, setBrandDescription] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [marketSegment, setMarketSegment] = useState("");
  const [products, setProducts] = useState<string[]>([]);
  const [competitors, setCompetitors] = useState<string[]>([]);
  const [brandKeywords, setBrandKeywords] = useState<string[]>([]);
  const [messagingGuidelines, setMessagingGuidelines] = useState("");
  const [socialPlatforms, setSocialPlatforms] = useState<string[]>([]);
  const [postingFrequency, setPostingFrequency] = useState("Daily");

  // Input state for dynamic lists
  const [productInput, setProductInput] = useState("");
  const [competitorInput, setCompetitorInput] = useState("");
  const [keywordInput, setKeywordInput] = useState("");

  const toneOptions = ["Professional", "Friendly", "Bold", "Luxury", "Playful", "Technical"];
  const platforms = ["Instagram", "LinkedIn", "X (Twitter)", "YouTube", "Facebook"];
  const frequencies = ["Daily", "3 times a week", "Weekly", "Custom"];

  const addProduct = () => {
    if (productInput.trim() && !products.includes(productInput.trim())) {
      setProducts([...products, productInput.trim()]);
      setProductInput("");
    }
  };

  const removeProduct = (product: string) => {
    setProducts(products.filter(p => p !== product));
  };

  const addCompetitor = () => {
    if (competitorInput.trim() && !competitors.includes(competitorInput.trim())) {
      setCompetitors([...competitors, competitorInput.trim()]);
      setCompetitorInput("");
    }
  };

  const removeCompetitor = (competitor: string) => {
    setCompetitors(competitors.filter(c => c !== competitor));
  };

  const addKeyword = () => {
    if (keywordInput.trim() && !brandKeywords.includes(keywordInput.trim())) {
      setBrandKeywords([...brandKeywords, keywordInput.trim()]);
      setKeywordInput("");
    }
  };

  const removeKeyword = (keyword: string) => {
    setBrandKeywords(brandKeywords.filter(k => k !== keyword));
  };

  const togglePlatform = (platform: string) => {
    if (socialPlatforms.includes(platform)) {
      setSocialPlatforms(socialPlatforms.filter(p => p !== platform));
    } else {
      setSocialPlatforms([...socialPlatforms, platform]);
    }
  };

  const handleSave = () => {
    // TODO: Implement save logic
    console.log("Saving settings...");
  };

  const handleReset = () => {
    setBrandName("");
    setBrandTone("Professional");
    setBrandDescription("");
    setTargetAudience("");
    setMarketSegment("");
    setProducts([]);
    setCompetitors([]);
    setBrandKeywords([]);
    setMessagingGuidelines("");
    setSocialPlatforms([]);
    setPostingFrequency("Daily");
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA] dark:bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-white/80 dark:bg-card/50 backdrop-blur-sm">
        <div className="max-w-[1600px] mx-auto px-8 py-4 flex items-center justify-between">
          <Link to="/" className="text-lg font-bold text-foreground">
            MarkitAI
          </Link>
          
          <div className="flex items-center gap-3">
            <Link 
              to="/dashboard" 
              className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Dashboard
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-8 py-5">
        {/* Page Header */}
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground mb-1">Brand Settings</h1>
            <p className="text-muted-foreground text-sm">
              Configure your brand intelligence for the AI Council.
            </p>
          </div>
        </div>

        {/* Three Column Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">{/* Brand Identity */}
          <div className="bg-white dark:bg-card rounded-2xl p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-sm border-0">
            <div className="mb-3">
              <h2 className="text-base font-bold text-foreground mb-0.5">Brand Identity</h2>
              <p className="text-xs text-muted-foreground">Core brand characteristics</p>
              <div className="h-px bg-gradient-to-r from-border to-transparent mt-2"></div>
            </div>
            
            <div className="space-y-3">
              {/* Brand Name + Brand Tone in one row */}
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label htmlFor="brand-name" className="block text-xs font-medium text-foreground mb-1.5">
                    Brand Name
                  </label>
                  <input
                    id="brand-name"
                    type="text"
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200"
                    placeholder="Acme Corp"
                  />
                </div>

                <div>
                  <label htmlFor="brand-tone" className="block text-xs font-medium text-foreground mb-1.5">
                    Brand Tone
                  </label>
                  <select
                    id="brand-tone"
                    value={brandTone}
                    onChange={(e) => setBrandTone(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200"
                  >
                    {toneOptions.map(tone => (
                      <option key={tone} value={tone}>{tone}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Brand Description */}
              <div>
                <label htmlFor="brand-description" className="block text-xs font-medium text-foreground mb-1.5">
                  Brand Description
                </label>
                <textarea
                  id="brand-description"
                  value={brandDescription}
                  onChange={(e) => setBrandDescription(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200 resize-none"
                  placeholder="Mission and values..."
                />
              </div>
            </div>
          </div>

          {/* Audience & Market */}
          <div className="bg-white dark:bg-card rounded-2xl p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-sm border-0">
            <div className="mb-3">
              <h2 className="text-base font-bold text-foreground mb-0.5">Audience & Market</h2>
              <p className="text-xs text-muted-foreground">Target audience and position</p>
              <div className="h-px bg-gradient-to-r from-border to-transparent mt-2"></div>
            </div>
            
            <div className="space-y-3">
              {/* Target Audience */}
              <div>
                <label htmlFor="target-audience" className="block text-xs font-medium text-foreground mb-1.5">
                  Target Audience
                </label>
                <textarea
                  id="target-audience"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200 resize-none"
                  placeholder="Demographics, interests..."
                />
              </div>

              {/* Market Segment */}
              <div>
                <label htmlFor="market-segment" className="block text-xs font-medium text-foreground mb-1.5">
                  Market Segment
                </label>
                <input
                  id="market-segment"
                  type="text"
                  value={marketSegment}
                  onChange={(e) => setMarketSegment(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200"
                  placeholder="B2B SaaS, E-commerce"
                />
              </div>
            </div>
          </div>

          {/* Products */}
          <div className="bg-white dark:bg-card rounded-2xl p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-sm border-0">
            <div className="mb-3">
              <h2 className="text-base font-bold text-foreground mb-0.5">Products</h2>
              <p className="text-xs text-muted-foreground">Your product offerings</p>
              <div className="h-px bg-gradient-to-r from-border to-transparent mt-2"></div>
            </div>
            
            <div className="space-y-3">
              <div>
                <label htmlFor="products" className="block text-xs font-medium text-foreground mb-1.5">
                  Product List
                </label>
                
                <div className="flex gap-2 mb-2">
                  <input
                    id="products"
                    type="text"
                    value={productInput}
                    onChange={(e) => setProductInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === 'Tab') {
                        e.preventDefault();
                        addProduct();
                      }
                    }}
                    className="flex-1 px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200"
                    placeholder="Product name"
                  />
                  <button
                    onClick={addProduct}
                    className="px-3 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-xl transition-all duration-200"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>

                {products.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {products.map(product => (
                      <span
                        key={product}
                        className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-primary/10 text-primary rounded text-xs border border-primary/20"
                      >
                        {product}
                        <button
                          onClick={() => removeProduct(product)}
                          className="hover:text-primary/70 transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Competitors */}
          <div className="bg-white dark:bg-card rounded-2xl p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-sm border-0">
            <div className="mb-3">
              <h2 className="text-base font-bold text-foreground mb-0.5">Competition</h2>
              <p className="text-xs text-muted-foreground">Competitive landscape</p>
              <div className="h-px bg-gradient-to-r from-border to-transparent mt-2"></div>
            </div>
            
            <div className="space-y-3">
              <div>
                <label htmlFor="competitors" className="block text-xs font-medium text-foreground mb-1.5">
                  Competitors
                </label>
                
                <div className="flex gap-2 mb-2">
                  <input
                    id="competitors"
                    type="text"
                    value={competitorInput}
                    onChange={(e) => setCompetitorInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === 'Tab') {
                        e.preventDefault();
                        addCompetitor();
                      }
                    }}
                    className="flex-1 px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200"
                    placeholder="Competitor name"
                  />
                  <button
                    onClick={addCompetitor}
                    className="px-3 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-xl transition-all duration-200"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>

                {competitors.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {competitors.map(competitor => (
                      <span
                        key={competitor}
                        className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-muted text-muted-foreground rounded text-xs border border-border"
                      >
                        {competitor}
                        <button
                          onClick={() => removeCompetitor(competitor)}
                          className="hover:text-foreground transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Keywords */}
          <div className="bg-white dark:bg-card rounded-2xl p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-sm border-0">
            <div className="mb-3">
              <h2 className="text-base font-bold text-foreground mb-0.5">Keywords</h2>
              <p className="text-xs text-muted-foreground">Brand keywords</p>
              <div className="h-px bg-gradient-to-r from-border to-transparent mt-2"></div>
            </div>
            
            <div className="space-y-3">
              <div>
                <label htmlFor="keywords" className="block text-xs font-medium text-foreground mb-1.5">
                  Brand Keywords
                </label>
                
                <div className="flex gap-2 mb-2">
                  <input
                    id="keywords"
                    type="text"
                    value={keywordInput}
                    onChange={(e) => setKeywordInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === 'Tab') {
                        e.preventDefault();
                        addKeyword();
                      }
                    }}
                    className="flex-1 px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200"
                    placeholder="Keyword"
                  />
                  <button
                    onClick={addKeyword}
                    className="px-3 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-xl transition-all duration-200"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>

                {brandKeywords.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {brandKeywords.map(keyword => (
                      <span
                        key={keyword}
                        className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-primary/10 text-primary rounded text-xs border border-primary/20"
                      >
                        {keyword}
                        <button
                          onClick={() => removeKeyword(keyword)}
                          className="hover:text-primary/70 transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Messaging Guidelines */}
          <div className="bg-white dark:bg-card rounded-2xl p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-sm border-0">
            <div className="mb-3">
              <h2 className="text-base font-bold text-foreground mb-0.5">Messaging</h2>
              <p className="text-xs text-muted-foreground">Brand voice guidelines</p>
              <div className="h-px bg-gradient-to-r from-border to-transparent mt-2"></div>
            </div>
            
            <div>
              <label htmlFor="messaging-guidelines" className="block text-xs font-medium text-foreground mb-1.5">
                Guidelines
              </label>
              <textarea
                id="messaging-guidelines"
                value={messagingGuidelines}
                onChange={(e) => setMessagingGuidelines(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground placeholder-muted-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200 resize-none"
                placeholder="Voice rules, topics to avoid..."
              />
            </div>
          </div>
        </div>

        {/* Platforms & Posting - Full Width Bottom Row */}
        <div className="grid grid-cols-1 gap-4">
          <div className="bg-white dark:bg-card rounded-2xl p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-sm border-0">
            <div className="mb-3">
              <h2 className="text-base font-bold text-foreground mb-0.5">Platforms & Posting Strategy</h2>
              <p className="text-xs text-muted-foreground">Configure where and how often to publish</p>
              <div className="h-px bg-gradient-to-r from-border to-transparent mt-2"></div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Social Platforms as Pills */}
              <div>
                <label className="block text-xs font-medium text-foreground mb-2">
                  Social Platforms
                </label>
                
                <div className="flex flex-wrap gap-2">
                  {platforms.map(platform => (
                    <button
                      key={platform}
                      onClick={() => togglePlatform(platform)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 border ${
                        socialPlatforms.includes(platform)
                          ? 'bg-[#3B82F6] border-[#3B82F6] text-white shadow-sm'
                          : 'bg-white dark:bg-background border-border/50 text-foreground hover:border-[#3B82F6]/30'
                      }`}
                    >
                      {platform}
                    </button>
                  ))}
                </div>
              </div>

              {/* Posting Frequency */}
              <div>
                <label htmlFor="posting-frequency" className="block text-xs font-medium text-foreground mb-2">
                  Posting Frequency
                </label>
                <select
                  id="posting-frequency"
                  value={postingFrequency}
                  onChange={(e) => setPostingFrequency(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-white dark:bg-background border-0 rounded-xl text-foreground shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:shadow-[inset_0_1px_2px_rgba(0,0,0,0.05),0_0_0_3px_rgba(59,130,246,0.1)] transition-all duration-200"
                >
                  {frequencies.map(freq => (
                    <option key={freq} value={freq}>{freq}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
        
        {/* Sticky Save Bar */}
        <div className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-card/80 backdrop-blur-lg border-t border-border/50 shadow-[0_-2px_8px_rgba(0,0,0,0.04)] z-40">
          <div className="max-w-[1600px] mx-auto px-8 py-2.5 flex items-center justify-between">
            <p className="text-xs text-muted-foreground">Make sure to save your changes before leaving</p>
            <div className="flex items-center gap-2">
              <button
                onClick={handleReset}
                className="px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground hover:bg-accent/50 rounded-lg transition-all duration-200 inline-flex items-center gap-1.5 border border-border/50"
              >
                <RotateCcw className="w-3 h-3" />
                Reset All
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-1.5 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium text-xs transition-all duration-200 inline-flex items-center gap-1.5 shadow-sm"
              >
                <Save className="w-3 h-3" />
                Save Changes
              </button>
            </div>
          </div>
        </div>
        
        {/* Bottom spacing for sticky bar */}
        <div className="h-12"></div>
      </div>
    </div>
  );
};

export default Settings;
