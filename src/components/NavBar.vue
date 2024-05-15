<template>
  <header class="site--header">
    <!-- Logo and link to home -->
    <router-link to="/" class="site--url" aria-label="18-tRNA therapeutics database">
      <img src="/logo.webp" class="avatar" alt="18-tRNA therapeutics database">
    </router-link>
    <!-- Navigation links -->
    <nav class="site--header__center">
      <ul class="topNav-items">
        <li><router-link to="/" active-class="active-link">Home</router-link></li>
        <li><router-link to="/coding-variation-disease" active-class="active-link">Coding Variation Disease</router-link></li>
        <li><router-link to="/TrnaElements" active-class="active-link">TrnaElements</router-link></li>
      </ul>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'NavBar'
}
</script>

<style>
@media (max-width: 768px) {
  .site--header {
    padding: 15px 20px; /* Reduced padding for smaller screens */
    flex-direction: column; /* Stack logo and menu vertically */
  }

  header.site--header {
        padding-top: 80px;
    }

  .site--header__center {
    position: static; /* Remove absolute positioning */
    transform: none;
    width: 100%; /* Full width */
    top: auto; /* Remove top positioning */
    box-shadow: none; /* Simplify style on smaller screens */
    border-radius: 0; /* Remove rounded corners */
    padding: 0; /* Remove additional padding */
  }

  .topNav-items {
    justify-content: center; /* Center menu items on small screens */
    overflow-x: auto; /* Allows horizontal scrolling on smaller screens */
    padding-left: 20px;
    padding-right: 20px;
  }

  .topNav-items li {
    padding: 10px; /* Adjust padding around links */
  }
}

@media (max-width: 820px) {
  .topNav-items {
    padding-left: 40px;
    padding-right: 40px;
  }
}

.site--header {
  padding: 20px 80px;
  position: relative;
  display: flex;
}

.site--url {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
  color: inherit; /* Inherit color, controlled by the parent element */
}

.site--url .avatar {
  margin-right: 10px;
  height: 48px;
  width: 48px;
  border: 3px solid var(--farallon-background-white);
  border-radius: 100%;
  box-shadow: 0 2px 4px 0 var(--farillon-border-color);
  transition: .5s ease-in-out;
}

.site--header__center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  height: 39px;
  top: 25px;
  z-index: 1;
  box-shadow: 0 0 #fff, 0 0 0 1px hsla(240, 5%, 96%, .1), 0 10px 15px -3px rgba(39, 39, 42, .05), 0 4px 6px -4px rgba(39, 39, 42, .05);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  background-color: hsla(0, 0%, 100%, .5);
  border: 1px solid hsla(0, 0%, 100%, .5);
  border-radius: 999rem;
  overflow: hidden;
}

.topNav-items {
  display: flex;
  align-items: center;
  height: 39px;
  box-sizing: border-box;
  padding: 5px 30px;
  margin: 0;
  list-style: none;
}

.topNav-items li {
  margin-right: 10px;
}

.topNav-items li a {
  color: rgba(0, 0, 0, 0.84); /* Default color, not selected */
  text-decoration: none; /* Remove underline */
}

.topNav-items li .active-link {
  color: #3a5f9a; /* Selected color */
}
</style>
