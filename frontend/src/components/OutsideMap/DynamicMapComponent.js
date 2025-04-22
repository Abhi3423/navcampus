'use client';

import dynamic from 'next/dynamic';

const DynamicMapComponent = dynamic(() => import('./MapComponent'), { ssr: false });

export default DynamicMapComponent;
