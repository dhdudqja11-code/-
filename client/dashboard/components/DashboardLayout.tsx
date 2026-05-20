import React from 'react';
import Link from 'next/link';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const Sidebar = () => (
  <div className="w-64 bg-gray-900 h-screen p-4 fixed top-0 left-0">
    <h1 className="text-2xl font-bold text-white mb-8">사업 기획소</h1>
    <nav>
      <Link href="/" className="block py-3 px-4 text-blue-400 hover:bg-gray-700 transition duration-150 border-l-4 border-blue-400">
        📊 대시보드 (Avoided Loss)
      </Link>
      <Link href="/settings" className="block py-3 px-4 text-gray-300 hover:bg-gray-700 transition duration-150">
        ⚙️ 시스템 설정
      </Link>
    </nav>
  </div>
);

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 ml-64 p-8">
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;