#ifndef LIGHT_H
#define LIGHT_H

#include <sys/types.h>

namespace hw
{
    class Light
    {
    public:
        static constexpr uint LIGHT_PIN {27};
        static constexpr uint LIGHT_ADC_INPUT {1};

        explicit Light();

        float measure();
    };
}

#endif // LIGHT_H