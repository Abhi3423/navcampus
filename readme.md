<br>
<p align="center">
<b>Hybrid Campus Navigation System
<br>
 The system employs an admin-controlled node finding using
 the RRT-Connect algorithm and storage mechanism, enabling
 real-time map updates and path optimizations. Pathfinding is
 handled through Dijkstra’s algorithm, ensuring optimal route
 generation, while an interactive 3D visualization module enhances
 user experience by displaying multi-floor navigation paths.
</b>
</p>

# 🚀 User Demo
      https://youtu.be/YwFrKSPNdH8

# 🚀 Admin System Demo

https://github.com/user-attachments/assets/c5b34745-8b7e-4bc9-a566-3bc8173aad77



# 💡  Problem Statement

Navigating large university campuses presents significant challenges due to the complexity of interconnected buildings, multiple floors, and varying environmental conditions. ✨🔥

# 💻 Tech Stack

* **Next.js**
* **Flask**
* **Tkinter**
* **TailwindCSS**
* **Supabase**

# Features

- **Hybrid Indoor-Outdoor Navigation:** Seamlessly transitions between outdoor and indoor routing, enabling uninterrupted guidance across campus environments.
- **Admin-Controlled Node System:** Admins use a dedicated Python GUI Desktop App to define, manage, and update navigation nodes, paths, and floor maps, enabling real-time map edits and rerouting.
- **RRT-Connect + Dijkstra's Algorithm:** Combines rapid random exploration (RRT-Connect) with optimal shortest path computation (Dijkstra’s), delivering efficient and accurate navigation in dynamic, multi-floor layouts.
- **3D Visualization Module:** Built using Trimesh and rendered in the browser with Three.js, the system provides interactive 3D models of buildings and paths to enhance spatial understanding and user experience.
- **Real-Time Rerouting:** Supports dynamic obstacle updates via the admin dashboard, instantly recalculating and displaying new paths for users to avoid blockages like construction or maintenance zones.
- **Parallelized Pathfinding:** Utilizes multi-threading to speed up node sampling and path generation, making the system responsive even in large-scale campus environments.
- **Supabase Database Integration:** Employs a PostgreSQL database for real-time updates of navigation data including rooms, nodes, and paths.
- **Frontend-Backend Sync:** A responsive Next.js frontend interacts with a Flask-based backend via RESTful APIs, allowing users to select buildings, floors, and destinations while receiving instant visual feedback.
- **Session-Based Routing Memory:** Users’ selections are temporarily stored in session storage, enabling persistent navigation during their session without repetitive inputs.
- **IEEE Published Research:** This system and its methodologies have been peer-reviewed and published by IEEE, validating its innovation and technical rigor.

# 📜 License

`It` is available under the MIT license. See the [`LICENSE`](https://opensource.org/license/mit/) file for more info.
