"use client";
import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";

export default function HomeScreen() {
  const router = useRouter();

  return (
    <div className="bg-base-100">
      <div className="navbar bg-base-100">
        <div className="navbar-start">
          <img
            className="mx-6 mt-3 mb-1 h-24 w-24 rounded-xl"
            src="/logo.png"
            alt="PDF GPT"
          />
        </div>
        <div className="navbar-center hidden lg:flex">
          <p className="block text-lg font-medium leading-6 text-slate-50">
            PDF GPT
          </p>
        </div>
        <div className="navbar-end">
          <a
            className="btn"
            onClick={() => {
              router.push("/login");
            }}
          >
            Login/Register
          </a>
        </div>
      </div>
      <div className="carousel w-full h-[650px]">
        <div id="slide1" className="carousel-item relative w-full">
          <img src="/carousel_1.jpg" className="w-full" />
          <div className="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
            <a href="#slide4" className="btn btn-circle">
              ❮
            </a>
            <a href="#slide2" className="btn btn-circle">
              ❯
            </a>
          </div>
        </div>
        <div id="slide2" className="carousel-item relative w-full">
          <img
            src="https://daisyui.com/images/stock/photo-1609621838510-5ad474b7d25d.jpg"
            className="w-full"
          />
          <div className="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
            <a href="#slide1" className="btn btn-circle">
              ❮
            </a>
            <a href="#slide3" className="btn btn-circle">
              ❯
            </a>
          </div>
        </div>
        <div id="slide3" className="carousel-item relative w-full">
          <img
            src="https://daisyui.com/images/stock/photo-1414694762283-acccc27bca85.jpg"
            className="w-full"
          />
          <div className="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
            <a href="#slide2" className="btn btn-circle">
              ❮
            </a>
            <a href="#slide4" className="btn btn-circle">
              ❯
            </a>
          </div>
        </div>
        <div id="slide4" className="carousel-item relative w-full">
          <img
            src="https://daisyui.com/images/stock/photo-1665553365602-b2fb8e5d1707.jpg"
            className="w-full"
          />
          <div className="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
            <a href="#slide3" className="btn btn-circle">
              ❮
            </a>
            <a href="#slide1" className="btn btn-circle">
              ❯
            </a>
          </div>
        </div>
      </div>
      <div className="card lg:card-side bg-base-100 shadow-xl mt-5">
        <img
          src="/busy_professional.jpg"
          alt="Technology"
          className="w-4/5 h-96 mx-20 my-5 rounded-xl"
        />
        <div className="card-body">
          <h2 className="card-title">Introducting PDF GPT!</h2>
          <p className="block text-lg font-medium leading-6 text-slate-50 leading-10	">
            Introducing PDF GPT - your solution for summarizing any document,
            anytime! In today's fast-paced world, finding peace amidst the chaos
            is essential. With PDF GPT, you can distill lengthy reports or
            articles into concise summaries effortlessly. Whether you're a
            student, professional, or just someone valuing time, PDF GPT
            streamlines your workload. Upload your document, let our AI analyze,
            and get a comprehensive summary quickly. Accessible on any device,
            PDF GPT ensures stress-free reading tasks. Embrace efficiency and
            tranquility with PDF GPT!
          </p>
        </div>
      </div>
      <footer className="footer p-10 bg-base-200 text-base-content">
        <aside>
          <img src="/logo.png" className="h-24 w-24 rounded-xl"></img>
          <p>
            PDF GPT.
            <br />
            Providing reliable tech since 2024
          </p>
        </aside>
      </footer>
    </div>
  );
}
