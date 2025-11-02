import React from "react";

const Hero = ({ setCurrentView, setShowChatBot, onDashboardAccess }) => {
  const handleGetStarted = () => {
    onDashboardAccess();
  };

  const handleWatchDemo = () => {
    setShowChatBot(true);
  };

  return (
    <section className="gradient-bg py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Your Smart
            <span className="text-sky-600"> Financial </span>
            Assistant
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Harness the power of AI to manage your finances, track expenses, and
            make informed investment decisions. Get personalized insights and
            recommendations tailored just for you.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={handleGetStarted}
              className="btn-primary text-lg px-8 py-4 hover:scale-105 transform transition-all duration-200"
            >
              Start Your Journey
            </button>
            <button
              onClick={handleWatchDemo}
              className="btn-secondary text-lg px-8 py-4 hover:scale-105 transform transition-all duration-200"
            >
              Watch Demo
            </button>
          </div>
        </div>

        {/* Hero Visual */}
        <div className="mt-16 relative">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Sample Dashboard Cards */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-green-800">
                    Total Savings
                  </h3>
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                </div>
                <p className="text-2xl font-bold text-green-800">$24,580</p>
                <p className="text-sm text-green-600">+12% this month</p>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-blue-800">Investments</h3>
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-2xl font-bold text-blue-800">$45,230</p>
                <p className="text-sm text-blue-600">Portfolio growing</p>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-purple-800">AI Insights</h3>
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                </div>
                <p className="text-2xl font-bold text-purple-800">95%</p>
                <p className="text-sm text-purple-600">Accuracy score</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
