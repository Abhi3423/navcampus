import React from 'react'
import missionImg from '../../../public/assets/mission.png'
import visionImg from '../../../public/assets/vision.png'
import Image from 'next/image'
import { FooterComponent } from '../Footer'
import { Button } from 'flowbite-react'


function AboutUs() {
    return (
        <div>
            <main className="flex flex-col pt-20 gap-16 mx-auto">
                {/* About Us */}
                <section className="flex flex-col items-center text-center gap-6 max-w-2xl mx-auto">
                    <h1 className="text-4xl md:text-6xl font-bold text-[#337AB7]">Hybrid Navigation System</h1>
                    <p className="text-lg md:text-xl leading-8 text-gray-700">
                        Our mission is to eliminate confusion, reduce search time, and provide effortless navigation across complex campuses.
                        Whether you're a student or visitor in a campus, our hybrid indoor-outdoor pathfinding and real-time 3D maps guide you to your destination — fast, easy, and intuitively.
                    </p>
                </section>

                {/* Inspiration */}
                <section className="bg-[#337AB7] text-white py-12 px-6 text-center">
                    <h2 className="text-3xl md:text-5xl font-bold mb-4">Inspiration</h2>
                    <p className="text-lg md:text-xl leading-8 max-w-3xl mx-auto">
                        Inspired by the everyday navigation struggles on large university campuses, we set out to build a seamless, intuitive experience.
                        From research halls to tech parks, we designed a system that understands structure, adapts in real time, and transforms how people explore space.
                        Our journey began at SRM with a vision: to redefine movement within complex environments.
                    </p>
                </section>

                {/* Mission and Vision */}
                <section className="flex flex-col gap-12 items-center text-center px-4">
                    <div className="flex flex-col md:flex-row-reverse items-center gap-8 max-w-5xl">
                        <div className="w-full md:w-1/2">
                            <Image src={missionImg} alt="Our Mission" width={500} height={500} className="mx-auto" />
                        </div>
                        <div className="w-full md:w-1/2">
                            <h2 className="text-3xl md:text-4xl font-bold text-[#337AB7] mb-4">Our Mission</h2>
                            <p className="text-lg leading-8 text-gray-700">
                                To revolutionize how people navigate through complex infrastructures — by combining indoor and outdoor mapping, dynamic route adjustment, and immersive 3D visualizations into one powerful platform.
                                Our system empowers institutions to provide smarter, safer, and more accessible guidance to all.
                            </p>
                        </div>
                    </div>

                    <div className="flex flex-col md:flex-row items-center gap-8 max-w-5xl">
                        <div className="w-full md:w-1/2">
                            <Image src={visionImg} alt="Our Vision" width={500} height={500} className="mx-auto" />
                        </div>
                        <div className="w-full md:w-1/2">
                            <h2 className="text-3xl md:text-4xl font-bold text-[#337AB7] mb-4">Our Vision</h2>
                            <p className="text-lg leading-8 text-gray-700">
                                We envision a future where no one gets lost in campus — where every student, visitor, or staff member walks with confidence.
                                With live rerouting and according to new obstacle updated path, and a commitment to universal accessibility, we aim to be the digital compass for smart campuses everywhere.
                            </p>
                        </div>
                    </div>
                </section>


                {/* Ready to Start */}
                <section className="flex flex-col items-center justify-center gap-6 py-12">
                    <div className="text-2xl md:text-3xl font-normal text-center md:text-left">
                        Ready to Start? Navigate Campus with Ease!
                    </div>

                    <div className='flex'>
                        <a href="/new-path-finder">
                            <Button className="transform hover:scale-125 transition duration-300 ease-in-out" outline color="light">
                                Path Finder
                            </Button>
                        </a>
                    </div>
                </section>

                <FooterComponent />
            </main>
        </div>
    )
}

export default AboutUs
