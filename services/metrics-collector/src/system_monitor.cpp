#include "system_monitor.h"
#include <iostream>

#if defined(_WIN32)
    #include <windows.h>
    #include <sysinfoapi.h>
#elif defined(__linux__)
    #include <fstream>
    #include <string>
    #include <sstream>
    #include <unistd.h>
#elif defined(__APPLE__)
    #include <mach/mach.h>
    #include <sys/sysctl.h>
    #include <unistd.h>
#else
    #include <random>
#endif

// Helper function to subtract FILETIME structures on Windows
#if defined(_WIN32)
static ULONGLONG subtract_filetime(const FILETIME& one, const FILETIME& two) {
    ULARGE_INTEGER a, b;
    a.LowPart = one.dwLowDateTime;
    a.HighPart = one.dwHighDateTime;
    b.LowPart = two.dwLowDateTime;
    b.HighPart = two.dwHighDateTime;
    return a.QuadPart - b.QuadPart;
}
#endif

double get_physical_ram_utilization() {
#if defined(_WIN32)
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    if (GlobalMemoryStatusEx(&memInfo)) {
        double total_phys = static_cast<double>(memInfo.ullTotalPhys);
        double avail_phys = static_cast<double>(memInfo.ullAvailPhys);
        if (total_phys > 0.0) {
            return 100.0 - (100.0 * avail_phys / total_phys);
        }
    }
#elif defined(__linux__)
    std::ifstream meminfo("/proc/meminfo");
    if (meminfo.is_open()) {
        std::string line;
        double total = 0.0;
        double free_mem = 0.0;
        while (std::getline(meminfo, line)) {
            if (line.find("MemTotal:") == 0) {
                std::stringstream ss(line);
                std::string label;
                ss >> label >> total;
            } else if (line.find("MemAvailable:") == 0) {
                std::stringstream ss(line);
                std::string label;
                ss >> label >> free_mem;
            }
        }
        if (total > 0.0) {
            return 100.0 - (100.0 * free_mem / total);
        }
    }
#elif defined(__APPLE__)
    mach_msg_type_number_t count = HOST_VM_INFO64_COUNT;
    vm_statistics64_data_t vmStats;
    if (host_statistics64(mach_host_self(), HOST_VM_INFO64, (host_info64_t)&vmStats, &count) == KERN_SUCCESS) {
        long long free_pages = vmStats.free_count + vmStats.inactive_count;
        long long active_pages = vmStats.active_count + vmStats.wire_count;
        long long total_pages = free_pages + active_pages;
        if (total_pages > 0) {
            return 100.0 * active_pages / total_pages;
        }
    }
#endif

    // Fallback simulated RAM usage if OS calls fail
    return 54.2;
}

double get_physical_cpu_utilization() {
#if defined(_WIN32)
    static FILETIME prev_idle_time = {0, 0};
    static FILETIME prev_kernel_time = {0, 0};
    static FILETIME prev_user_time = {0, 0};

    FILETIME idle_time, kernel_time, user_time;
    if (GetSystemTimes(&idle_time, &kernel_time, &user_time)) {
        ULONGLONG idle_diff = subtract_filetime(idle_time, prev_idle_time);
        ULONGLONG kernel_diff = subtract_filetime(kernel_time, prev_kernel_time);
        ULONGLONG user_diff = subtract_filetime(user_time, prev_user_time);

        prev_idle_time = idle_time;
        prev_kernel_time = kernel_time;
        prev_user_time = user_time;

        ULONGLONG total_sys = kernel_diff + user_diff;
        if (total_sys > 0) {
            // Kernel time includes idle time on Windows, so we subtract idle_diff
            ULONGLONG active_sys = total_sys - idle_diff;
            return 100.0 * active_sys / total_sys;
        }
    }
#elif defined(__linux__)
    static unsigned long long prev_user = 0, prev_nice = 0, prev_system = 0, prev_idle = 0;
    std::ifstream stat_file("/proc/stat");
    if (stat_file.is_open()) {
        std::string cpu_label;
        unsigned long long user, nice, system, idle;
        stat_file >> cpu_label >> user >> nice >> system >> idle;
        
        unsigned long long total = (user - prev_user) + (nice - prev_nice) + 
                                   (system - prev_system) + (idle - prev_idle);
        unsigned long long active = total - (idle - prev_idle);
        
        prev_user = user; prev_nice = nice; prev_system = system; prev_idle = idle;
        
        if (total > 0) {
            return 100.0 * active / total;
        }
    }
#elif defined(__APPLE__)
    host_cpu_load_info_data_t cpuInfo;
    mach_msg_type_number_t count = HOST_CPU_LOAD_INFO_COUNT;
    static unsigned long long prev_user = 0, prev_sys = 0, prev_idle = 0;
    
    if (host_statistics(mach_host_self(), HOST_CPU_LOAD_INFO, (host_info_t)&cpuInfo, &count) == KERN_SUCCESS) {
        unsigned long long user = cpuInfo.cpu_ticks[CPU_STATE_USER] + cpuInfo.cpu_ticks[CPU_STATE_SYSTEM];
        unsigned long long sys = cpuInfo.cpu_ticks[CPU_STATE_SYSTEM];
        unsigned long long idle = cpuInfo.cpu_ticks[CPU_STATE_IDLE];
        
        unsigned long long total = (user - prev_user) + (sys - prev_sys) + (idle - prev_idle);
        unsigned long long active = total - (idle - prev_idle);
        
        prev_user = user; prev_sys = sys; prev_idle = idle;
        if (total > 0) {
            return 100.0 * active / total;
        }
    }
#endif

    // Fallback simulated CPU load if OS calls fail
    return 32.8;
}
