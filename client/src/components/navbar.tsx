import React from "react";
import Link from "next/link";

const Navbar: React.FC = () => {
  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex-shrink-0 flex items-center">
            <Link href="/" passHref>
              <span className="text-2xl font-bold text-primary">SlideProf</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;