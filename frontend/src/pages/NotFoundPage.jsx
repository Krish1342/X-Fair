/**
 * Not Found Page Component
 */
import React from "react";
import { useNavigate } from "react-router-dom";
import Button from "@ui/Button";

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* 404 Illustration */}
        <div className="mb-8">
          <div className="text-9xl font-bold text-blue-100 mb-4">404</div>
          <div className="text-6xl mb-4">🔍</div>
        </div>

        {/* Content */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Page Not Found
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Sorry, we couldn't find the page you're looking for. It might have
          been moved, deleted, or you entered the wrong URL.
        </p>

        {/* Action Buttons */}
        <div className="space-y-4">
          <Button onClick={() => navigate("/")} size="lg" className="w-full">
            Go to Homepage
          </Button>

          <Button
            onClick={() => navigate(-1)}
            variant="outline"
            size="lg"
            className="w-full"
          >
            Go Back
          </Button>
        </div>

        {/* Help Text */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            <strong>Need help?</strong> If you think this is a mistake, please
            contact our support team.
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
