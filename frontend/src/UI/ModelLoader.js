import React from 'react';
import styled from 'styled-components';

const ModelLoader = () => {
    return (
        <div className="flex w-full h-full text-center justify-center items-center">
            <StyledWrapper>
                <div className='flex flex-col items-center text-center justify-center'>
                    <div className="loader">
                        <div className="box box-1">
                            <div className="side-left" />
                            <div className="side-right" />
                            <div className="side-top" />
                        </div>
                        <div className="box box-2">
                            <div className="side-left" />
                            <div className="side-right" />
                            <div className="side-top" />
                        </div>
                        <div className="box box-3">
                            <div className="side-left" />
                            <div className="side-right" />
                            <div className="side-top" />
                        </div>
                        <div className="box box-4">
                            <div className="side-left" />
                            <div className="side-right" />
                            <div className="side-top" />
                        </div>
                    </div>
                    <div className="flex text-center self-center">Converting to 3d...</div>
                </div>
            </StyledWrapper>
        </div>
    );
}

const StyledWrapper = styled.div`
  /* 3D tower loader made by: csozi | Website: www.csozi.hu*/

  .loader {
    scale: 3;
    height: 50px;
    width: 40px;
  }

  .box {
    position: relative;
    opacity: 0;
    left: 10px;
  }

  .side-left {
    position: absolute;
    background-color: #286cb5;
    width: 19px;
    height: 5px;
    transform: skew(0deg, -25deg);
    top: 14px;
    left: 10px;
  }

  .side-right {
    position: absolute;
    background-color: #2f85e0;
    width: 19px;
    height: 5px;
    transform: skew(0deg, 25deg);
    top: 14px;
    left: -9px;
  }

  .side-top {
    position: absolute;
    background-color: #5fa8f5;
    width: 20px;
    height: 20px;
    rotate: 45deg;
    transform: skew(-20deg, -20deg);
  }

  .box-1 {
    animation: from-left 4s infinite;
  }

  .box-2 {
    animation: from-right 4s infinite;
    animation-delay: 1s;
  }

  .box-3 {
    animation: from-left 4s infinite;
    animation-delay: 2s;
  }

  .box-4 {
    animation: from-right 4s infinite;
    animation-delay: 3s;
  }

  @keyframes from-left {
    0% {
      z-index: 20;
      opacity: 0;
      translate: -20px -6px;
    }

    20% {
      z-index: 10;
      opacity: 1;
      translate: 0px 0px;
    }

    40% {
      z-index: 9;
      translate: 0px 4px;
    }

    60% {
      z-index: 8;
      translate: 0px 8px;
    }

    80% {
      z-index: 7;
      opacity: 1;
      translate: 0px 12px;
    }

    100% {
      z-index: 5;
      translate: 0px 30px;
      opacity: 0;
    }
  }

  @keyframes from-right {
    0% {
      z-index: 20;
      opacity: 0;
      translate: 20px -6px;
    }

    20% {
      z-index: 10;
      opacity: 1;
      translate: 0px 0px;
    }

    40% {
      z-index: 9;
      translate: 0px 4px;
    }

    60% {
      z-index: 8;
      translate: 0px 8px;
    }

    80% {
      z-index: 7;
      opacity: 1;
      translate: 0px 12px;
    }

    100% {
      z-index: 5;
      translate: 0px 30px;
      opacity: 0;
    }
  }`;

export default ModelLoader;
