import { Inter } from "next/font/google";
import "./globals.css";
import Link from 'next/link';
import Image from "next/image";
import { Navbar, NavbarBrand, NavbarCollapse, NavbarLink, NavbarToggle } from 'flowbite-react';

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "SRMIST 3D MAP",
  description: "Generated by create next app",
};

export default function RootLayout({ children }) {
  const navbtnclass = "px-5 py-3 rounded-md hover:shadow-lg hover:drop-shadow-lg border-2 border-[#337AB7] hover:bg-[#337AB7] text-[#337AB7] hover:text-white"
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar fluid rounded>
          <NavbarBrand as={Link} href="/">
            <Image src="/assets/srmist.jpg" width={150} height={10} className="mr-3 h-9" alt="SRM Logo" />
            {/* <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">Flowbite React</span> */}
          </NavbarBrand>
          <NavbarToggle />
          <NavbarCollapse>
            <NavbarLink href="/">
              <div className={navbtnclass}>Home</div>
            </NavbarLink>
            <NavbarLink as={Link} href="about-us">
              <div className={navbtnclass}>About</div>
            </NavbarLink>
            <NavbarLink as={Link} href="information">
              <div className={navbtnclass}>Information</div>
            </NavbarLink>
            <NavbarLink as={Link} href="https://github.com/Abhi3423/navcampus">
              <div className={navbtnclass}>View Github</div>
            </NavbarLink>
            <NavbarLink as={Link} href="https://ieeexplore.ieee.org/document/10894337">
              <div className={navbtnclass}>View Research Paper</div>
            </NavbarLink>
          </NavbarCollapse>
        </Navbar>
        {children}
      </body>
    </html>
  );
}
