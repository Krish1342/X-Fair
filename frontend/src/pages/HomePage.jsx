import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@ui";

export default function HomePage() {
  const features = [
    {
      icon: "🤖",
      title: "AI-Powered Insights",
      description:
        "Get personalized financial advice from our intelligent assistant.",
    },
    {
      icon: "💰",
      title: "Smart Budgeting",
      description:
        "Automatically categorize expenses and optimize your spending.",
    },
    {
      icon: "📊",
      title: "Investment Tracking",
      description:
        "Monitor your portfolio performance with real-time analytics.",
    },
    {
      icon: "🎯",
      title: "Goal Planning",
      description: "Set and achieve your financial goals with guided planning.",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-white">
        <div className="max-w-7xl mx-auto px-6 py-20 lg:flex lg:items-center lg:gap-12">
          <div className="mx-auto max-w-2xl lg:mx-0">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
              Take Control of Your{" "}
              <span className="text-blue-600">Financial Future</span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Transform your financial life with our AI-powered personal finance
              agent. Get personalized insights, smart budgeting, and investment
              recommendations tailored just for you.
            </p>
            <div className="mt-10 flex items-center gap-x-6">
              <Link
                to="/login"
                className="rounded-md bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
              >
                Get Started Free →
              </Link>
              <button className="text-sm font-semibold leading-6 text-gray-900">
                Watch Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">
              Powerful Features for Your Financial Success
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
              Discover how our advanced AI technology and intuitive design can
              help you achieve your goals faster.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="rounded-xl border bg-white p-6 shadow-sm"
              >
                <div className="text-3xl">{feature.icon}</div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative bg-gradient-to-r from-blue-600 to-purple-600 py-16">
        <div className="max-w-7xl mx-auto px-6 text-center text-white">
          <h2 className="text-3xl font-bold">
            Ready to Transform Your Financial Future?
          </h2>
          <p className="mt-4 text-blue-100 max-w-3xl mx-auto">
            Join thousands of users who have already taken control of their
            finances with our AI-powered platform.
          </p>
          <div className="mt-8 flex justify-center">
            <Link
              to="/login"
              className="rounded-md bg-white px-6 py-3 text-sm font-semibold text-blue-700 shadow-sm hover:bg-blue-50"
            >
              Start Your Journey Today →
            </Link>
          </div>
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center justify-center gap-3">
              <span className="text-green-300 text-xl">✓</span>
              <span className="text-blue-100">Free to get started</span>
            </div>
            <div className="flex items-center justify-center gap-3">
              <span className="text-green-300 text-xl">✓</span>
              <span className="text-blue-100">No credit card required</span>
            </div>
            <div className="flex items-center justify-center gap-3">
              <span className="text-green-300 text-xl">✓</span>
              <span className="text-blue-100">Cancel anytime</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
