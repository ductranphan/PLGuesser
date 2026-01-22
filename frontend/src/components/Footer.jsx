/**
 * Footer - Displays at the bottom of every page
 */
function Footer() {
  return (
    <footer className="py-6 mt-8">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <p className="text-gray-600 text-sm">
          © 2026 PLGuesser. Built by a Developer, for Everyone.
        </p>
        <p className="text-gray-600 text-xs mt-2">
          Created by{' '}
          <a
            href="https://www.linkedin.com/in/ductranphan/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-700 hover:text-gray-800 underline transition-colors"
          >
            DucTranPhan
          </a>
        </p>
      </div>
    </footer>
  );
}

export default Footer;
