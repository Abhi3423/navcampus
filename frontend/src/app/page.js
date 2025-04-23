"use client"
import Image from "next/image";
import location from "../../public/assets/image.png";
import HowItWorks from "../../public/assets/HowItWorks.png";
import { Button } from 'flowbite-react';
import Textborder from "@/UI/textborder";
import { FooterComponent } from "./Footer";
import { EXTERNAL_PATH_URL } from "@/utils/constants/const";
import { useEffect } from "react";

export default function Home() {

  useEffect(() => {
    const RunServer = async () => {
      try {
        
        const response = await fetch(`${EXTERNAL_PATH_URL}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }

        const responseData = await response.json();
        console.log(responseData.data);
        
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    RunServer();
  }, []);


  return (
    <main className="flex flex-col items-center">
      {/* Parallax background */}
      <div className="relative w-full h-screen">
        {/* Background image with blur effect */}
        <div
          className="absolute inset-0 bg-fixed bg-cover bg-center filter blur-[3px]"
          style={{ backgroundImage: `url('/assets/street.jpg')` }}
        ></div>

        {/* Content on top of the background image */}
        <div className="absolute inset-0 flex flex-col gap-4 justify-start items-center py-32 md:px-24 text-[#487dab] text-3xl md:text-6xl font-bold">
          <div className="flex items-center text-center px-20">
            <Textborder CustomBold="font-black" text="SRM M" />
            <Image className="z-10 w-12 h-14 animate-bounce" src={location} alt="location" />
            <Textborder CustomBold="font-black" text="P" />
          </div>
          <Textborder CustomBold="font-morebold" text="Shortest Path Finder" />
          <div className="flex md:px-40">
            <a href="/new-path-finder">
              <Button className="transform hover:scale-125 transition duration-300 ease-in-out" outline color="light">
                Path Finder
              </Button>
            </a>
          </div>
        </div>
      </div>

      {/* Content below the image */}

      <div className="flex flex-col py-12 w-[90%] justify-center items-center">
        <div className="font-medium text-gray-600 text-3xl"> HOW IT WORKS ? </div>
        <div className="w-[70%] text-lg text-center py-8"> With SRM MAP Path Finder, visitors can spend less time searching for building directories and more time discovering new points of interest. Simply select and find the way inside and outside the building.</div>
        <div className="flex flex-col md:flex-row gap-y-8 gap-x-4 py-5 text-center md:text-start">
          <div className="flex flex-col gap-y-6 md:gap-0 justify-between">

            <div className="flex flex-col gap-3">
              <div className="font-medium text-gray-600 text-xl">Select Floors to navigate</div>
              <div className="">Select the source and destination floor for a building and get your directions.</div>
            </div>
            <div className="flex flex-col gap-3">
              <div className="font-medium text-gray-600 text-xl">Improved location accuracy</div>
              <div className="">Digital directory in the easiest way.</div>
            </div>



          </div>

          {/* HOW IT WORKS LAPTOP IMAGE */}
          <div className="flex flex-col justify-between">
            <Image className=" md:max-w-xl" alt="" src={HowItWorks} />
          </div>

          <div className="flex flex-col gap-y-6 md:gap-0 justify-between">

            <div className="flex flex-col gap-3">
              <div className="font-medium text-gray-600 text-xl">Switch floors with a tap</div>
              <div className="">Use the level switcher in the bottom right-hand corner to move from floor to floor in the building.</div>
            </div>

            <div className="flex flex-col gap-3">
              <div className="font-medium text-gray-600 text-xl">Universal icons</div>
              <div className="">Easily recognizable symbols represent different points of interest inside.</div>
            </div>

          </div>

        </div>
      </div>

      <FooterComponent />
    </main>
  );
}
