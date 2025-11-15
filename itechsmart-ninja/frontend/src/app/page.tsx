export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            iTechSmart Ninja
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Autonomous AI Agents for IT Operations & Automation
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="/login"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Get Started
            </a>
            <a
              href="/about"
              className="px-6 py-3 bg-white text-blue-600 rounded-lg border border-blue-600 hover:bg-blue-50 transition"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>
    </main>
  )
}