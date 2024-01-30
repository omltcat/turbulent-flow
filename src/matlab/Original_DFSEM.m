%%%%%%%%%% Original Poletto DFSEM Method %%%%%%%%%%
tic
%%% Control Eddy/Grid Parameters %%%
step = 0.1;
lx = 1.0;
ly = 1.0;
lz = 1.0;
sx = 0.5;
sy = 0.5;
sz = 0.5;
N = 1;

%%% Define Eigenvector Rotation Matrix and Normalize %%%
Rot = eye(3);
% Rot = [-5.57256 0.13211 0.22226; 0.24728 -1.06676 0.96493; 1 1 1];
% Rot = [-1 1 0; 1 1 0; 0 0 1];
% phi = -0*pi()/8; theta = 0; psi = -0*pi()/4;
% phi = -3*pi()/4; theta = -0.955; psi = 0;
% phi = 0; theta = 0; psi = 0;
% Rx = [1 0 0; 0 cos(phi) -sin(phi); 0 sin(phi) cos(phi)];
% Ry = [cos(theta) 0  sin(theta); 0 1 0; -sin(theta) 0 cos(theta)];
% Rz = [cos(psi) -sin(psi) 0; sin(psi) cos(psi) 0; 0 0 1];
% Rot = Rz*Ry*Rx;
% Rot = [0.577 0.577 0.577; -0.577 0.789 -0.211; -0.577 -0.211 0.789];
% Rot = [-0.707 -0.707 0.577; 0 0.707 0.577; 0.707 0 0.577];
% Rot = [0.7887 -0.2113 0.5774; -0.2113 0.787 0.5774; -0.5774 -0.5774 0.5774];
abs1 = (sqrt(Rot(1,1)^2 + Rot(2,1)^2 + Rot(3,1)^2));
abs2 = (sqrt(Rot(1,2)^2 + Rot(2,2)^2 + Rot(3,2)^2));
abs3 = (sqrt(Rot(1,3)^2 + Rot(2,3)^2 + Rot(3,3)^2));
Rot(:,1) = Rot(:,1)./abs1;
Rot(:,2) = Rot(:,2)./abs2;
Rot(:,3) = Rot(:,3)./abs3;
iRot = inv(Rot);

offset = 0; % Control the region of averaging

%%% Generate Eddy Intensities %%% CHANGE BELOW TO MATCH ALFA FORMULA
%%% DIVISION BY SIGMAS
lamx = 1; lamy = 1; lamz = 1;
for i = 1:N
    alfx(i) = -sqrt(0);
    alfy(i) = -sqrt(0);
    alfz(i) = -sqrt(1);
%     s = sign(rand()-0.5);
%     alfx(i) = 1*s;
%     alfy(i) = 1*s;
%     alfz(i) = 1*s;
    %     alfx(i) = sqrt(0.5).*sign(rand()-0.5);
    %     alfy(i) = sqrt(1.5).*sign(rand()-0.5);
    %     alfz(i) = sqrt(1.5).*sign(rand()-0.5);
    %     alfx(i) = sqrt(1.8951).*sign(rand()-0.5);
    %     alfy(i) = sqrt(1.4262).*sign(rand()-0.5);
    %     alfz(i) = sqrt(13.9771).*sign(rand()-0.5);
%     alfx(i) = sqrt((lamx./(sx).^2) + (lamy./(sy).^2) + (lamz./(sz).^2) - 2*(lamx./(sx).^2));
%     alfy(i) = sqrt((lamx./(sx).^2) + (lamy./(sy).^2) + (lamz./(sz).^2) - 2*(lamy./(sy).^2));
%     alfz(i) = sqrt((lamx./(sx).^2) + (lamy./(sy).^2) + (lamz./(sz).^2) - 2*(lamz./(sz).^2));
%     alfx(i) = sqrt((lamx./(sx).^2) + (lamy./(sy).^2) + (lamz./(sz).^2) - 2*(lamx./(sx).^2)).*sign(rand()-0.5);
%     alfy(i) = sqrt((lamx./(sx).^2) + (lamy./(sy).^2) + (lamz./(sz).^2) - 2*(lamy./(sy).^2)).*sign(rand()-0.5);
%     alfz(i) = sqrt((lamx./(sx).^2) + (lamy./(sy).^2) + (lamz./(sz).^2) - 2*(lamz./(sz).^2)).*sign(rand()-0.5);
end
%%% %%%

%%% Grid Generation %%%
xa = -lx;
xb = lx;
nx = (xb-xa)./step + 1;
rx = xa:step:xb;

ya = -ly;
yb = ly;
ny = (yb-ya)./step + 1;
ry = ya:step:yb;

za = -lz;
zb = lz;
nz = (zb-za)./step + 1;
rz = za:step:zb;

% Define grid and rotate it
[x,y,z] = meshgrid(rx,ry,rz);
x2 = iRot(1,1)*x + iRot(1,2)*y + iRot(1,3)*z;
y2 = iRot(2,1)*x + iRot(2,2)*y + iRot(2,3)*z;
z2 = iRot(3,1)*x + iRot(3,2)*y + iRot(3,3)*z;
% x = x2;
% y = y2;
% z = z2;

Vb = (xb-xa)*(yb-ya)*(zb-za); % Volume of box
%%% %%%

%%% Randomize Eddy Location (uses circshift)
% xk = randi([0,nx-1],1,N);
% yk = randi([0,ny-1],1,N);
% zk = randi([0,nz-1],1,N);
xk(1) = 0;
yk(1) = 0;
zk(1) = 0;
% xk(2) = 0;
% yk(2) = 0;
% zk(2) = 0;
%%% %%%

%%% Calculate the General Velocity Field of the Eddy in the Center %%%

uf = zeros(nx,ny,nz);
vf = zeros(nx,ny,nz);
wf = zeros(nx,ny,nz);
ug = zeros(nx,ny,nz);
vg = zeros(nx,ny,nz);
wg = zeros(nx,ny,nz);

% Define a normalized distance from center
d = zeros(nx,ny,nz);
for i = 1:nx
    for j = 1:ny
        for k = 1:nz
            d(i,j,k) = sqrt(((x2(i,j,k))./sx).^2 + ((y2(i,j,k))./sy).^2 + ((z2(i,j,k))./sz).^2);
            if d(i,j,k) >= 1.0
                d(i,j,k) = 0;
            else
                d(i,j,k) = d(i,j,k);
            end
        end
    end
end

% Define shape function
qx = zeros(nx,ny,nz);
qy = zeros(nx,ny,nz);
qz = zeros(nx,ny,nz);
% B = sqrt(4.7*Vb*(sy.*(sx+sy+sz)./3)/(N.*sx.*sy.*sz));
% B = sqrt(10*Vb/N)*(sy.*(sx+sy+sz)./3)/(sx*sy*sz);
Bx = 1*sqrt((5*Vb/N)/(sx.*sy.*sz)); % Normalization constants
By = 1*sqrt((5*Vb/N)/(sx.*sy.*sz));
Bz = 1*sqrt((5*Vb/N)/(sx.*sy.*sz));
for i = 1:nx
    for j = 1:ny
        for k = 1:nz
            if d(i,j,k) == 0.0
                qx(i,j,k) = 0;
                qy(i,j,k) = 0;
                qz(i,j,k) = 0;
            else
                qx(i,j,k) = Bx.*(sx).*(1 - (d(i,j,k)).^2);
                qy(i,j,k) = By.*(sy).*(1 - (d(i,j,k)).^2);
                qz(i,j,k) = Bz.*(sz).*(1 - (d(i,j,k)).^2);
%                 qx(i,j,k) = Bx.*(sx).*exp(-6*(d(i,j,k)).^2);
%                 qy(i,j,k) = By.*(sy).*exp(-6*(d(i,j,k)).^2);
%                 qz(i,j,k) = Bz.*(sz).*exp(-6*(d(i,j,k)).^2);
            end
        end
    end
end

for eddy = 1:N

u = zeros(nx,ny,nz);
for i = 1:nx
    for j = 1:ny
        for k = 1:nz
            u(i,j,k) = qx(i,j,k).*(((y2(i,j,k))./sy).*alfz(eddy)-((z2(i,j,k))./sz).*alfy(eddy));
        end
    end
end

v = zeros(nx,ny,nz);
for i = 1:nx
    for j = 1:ny
        for k = 1:nz
            v(i,j,k) = qy(i,j,k).*(((z2(i,j,k))./sz).*alfx(eddy)-((x2(i,j,k))./sx).*alfz(eddy));
        end
    end
end

w = zeros(nx,ny,nz);
for i = 1:nx
    for j = 1:ny
        for k = 1:nz
            w(i,j,k) = qz(i,j,k).*(((x2(i,j,k))./sx).*alfy(eddy)-((y2(i,j,k))./sy).*alfx(eddy));
        end
    end
end

% Randomize eddy location
uf = uf + circshift(u,[yk(eddy), xk(eddy), zk(eddy)]);
vf = vf + circshift(v,[yk(eddy), xk(eddy), zk(eddy)]);
wf = wf + circshift(w,[yk(eddy), xk(eddy), zk(eddy)]);

end

% Rotate vectors
ug = Rot(1,1).*uf + Rot(1,2).*vf + Rot(1,3).*wf;
vg = Rot(2,1).*uf + Rot(2,2).*vf + Rot(2,3).*wf;
wg = Rot(3,1).*uf + Rot(3,2).*vf + Rot(3,3).*wf;

%%% %%%

%%% Analysis/Plotting %%%
% [x,y,z] = meshgrid(rx,ry,rz);
% quiver3(x,y,z,ug,vg,wg)
% xlabel('x')
% ylabel('y')
% zlabel('z')
% title('DFSEM 100 Eddies')

% quiver(x(:,:,((nx/2)+0.5)),y(:,:,((nx/2)+0.5)),ug(:,:,((nx/2)+0.5)),vg(:,:,((nx/2)+0.5)));
% [startx, starty] = meshgrid(-3:0.2:3,-3:0.2:3);
% hold on
% streamline(x(:,:,((nx/2)+0.5)),y(:,:,((nx/2)+0.5)),uf(:,:,((nx/2)+0.5)),vf(:,:,((nx/2)+0.5)),startx,starty)
% hold off
% xlabel('x')
% ylabel('y')
% title('DFSEM 2-D slice of 3-D Domain')

% legend('Non-DF','DF')
% div = divergence(x,y,z,ug,vg,wg);
% div = div(:,:,((nx/2)+0.5));
% max(max(max(div)));

% aut = abs(ifftn(fft(ug).*(conj(fft(ug)))))./(nx).^1;
% aut(1,1,1)
%%% %%%

uu = 0;
vv = 0;
ww = 0;
uv = 0;
uw = 0;
vw = 0;
for i = 1+offset:nx-offset
    for j = 1+offset:ny-offset
        for k = 1+offset:nz-offset
            uu = uu + ug(i,j,k).*ug(i,j,k)./((nx-2*offset).*(ny-2*offset).*(nz-2*offset));
            vv = vv + vg(i,j,k).*vg(i,j,k)./((nx-2*offset).*(ny-2*offset).*(nz-2*offset));
            ww = ww + wg(i,j,k).*wg(i,j,k)./((nx-2*offset).*(ny-2*offset).*(nz-2*offset));
            uv = uv + ug(i,j,k).*vg(i,j,k)./((nx-2*offset).*(ny-2*offset).*(nz-2*offset));
            uw = uw + ug(i,j,k).*wg(i,j,k)./((nx-2*offset).*(ny-2*offset).*(nz-2*offset));
            vw = vw + vg(i,j,k).*wg(i,j,k)./((nx-2*offset).*(ny-2*offset).*(nz-2*offset));
        end
    end
end

Rexp = [uu uv uw; uv vv vw; uw vw ww];

% Sample unit vector on plot
wx = zeros(nx,ny,nz); wy = zeros(nx,ny,nz); wz = zeros(nx,ny,nz); 
% phi = -3*pi()/4; theta = -0.955; psi = 0;
% Rx = [1 0 0; 0 cos(phi) -sin(phi); 0 sin(phi) cos(phi)];
% Ry = [cos(theta) 0  sin(theta); 0 1 0; -sin(theta) 0 cos(theta)];
% Rz = [cos(psi) -sin(psi) 0; sin(psi) cos(psi) 0; 0 0 1];
% R = Rz*Ry*Rx;
R = Rot;
% R = [-0.707 -0.707 0.577; 0 0.707 0.577; 0.707 0 0.577];
iR = R';
w = R*[0; 0; 1];
wx(round(nx/2),round(nx/2),round(nx/2)) = w(1,1); wy(round(nx/2),round(nx/2),round(nx/2)) = w(2,1); wz(round(nx/2),round(nx/2),round(nx/2)) = w(3,1);
% wx(round(nx/2),round(nx/2),round(nx/2)) = -alfx(1)*(sx); wy(round(nx/2),round(nx/2),round(nx/2)) = -alfy(1)*(sy); wz(round(nx/2),round(nx/2),round(nx/2)) = -alfz(1)*(sz);

% [curlx,curly,curlz,cav] = curl(x,y,z,ug,vg,wg);
% min(min(min(curlx)))
% min(min(min(curly)))
% min(min(min(curlz)))
%

%%%%%
% wx1 = zeros(nx,ny,nz); wy1 = zeros(nx,ny,nz); wz1 = zeros(nx,ny,nz);
% wx2 = zeros(nx,ny,nz); wy2 = zeros(nx,ny,nz); wz2 = zeros(nx,ny,nz);
% wx3 = zeros(nx,ny,nz); wy3 = zeros(nx,ny,nz); wz3 = zeros(nx,ny,nz);
% 
% w1 = [-0.707; 0; 0.707];
% wx1(round(nx/2),round(nx/2),round(nx/2)) = w1(1,1); wy1(round(nx/2),round(nx/2),round(nx/2)) = w1(2,1); wz1(round(nx/2),round(nx/2),round(nx/2)) = w1(3,1);
% 
% w2 = [-0.707; 0.707; 0];
% wx2(round(nx/2),round(nx/2),round(nx/2)) = w2(1,1); wy2(round(nx/2),round(nx/2),round(nx/2)) = w2(2,1); wz2(round(nx/2),round(nx/2),round(nx/2)) = w2(3,1);
% 
% w3 = [0.5774; 0.5774; 0.5774];
% wx3(round(nx/2),round(nx/2),round(nx/2)) = w3(1,1); wy3(round(nx/2),round(nx/2),round(nx/2)) = w3(2,1); wz3(round(nx/2),round(nx/2),round(nx/2)) = w3(3,1);
%%%%%


[x,y,z] = meshgrid(rx,ry,rz);
% quiver3(x,y,z,wx1,wy1,wz1,3)
% hold on
% quiver3(x,y,z,wx2,wy2,wz2,3)
% hold on
% quiver3(x,y,z,wx3,wy3,wz3,3)
% hold off
quiver3(x,y,z,ug,vg,wg)
% hold on
% quiver3(x,y,z,wx,wy,wz,3)
% hold off
% title('\overrightarrow{\omega} = (1,1,1), $${\sigma = (2,1,1)}$$, $${\alpha = (-1,-1,-1)}$$','Interpreter','Latex','FontSize',16)
xlabel('x','Interpreter','latex','FontSize',16)
ylabel('y','Interpreter','latex','FontSize',16)
zlabel('z','Interpreter','latex','FontSize',16)
set(gcf,'color','white')

% quiver(x(:,:,((nx/2)+0.5)),y(:,:,((nx/2)+0.5)),ug(:,:,((nx/2)+0.5)),vg(:,:,((nx/2)+0.5)),1);
% [startx, starty] = meshgrid(-3:0.2:3,-3:0.2:3);
% hold on
% streamline(x(:,:,((nx/2)+0.5)),y(:,:,((nx/2)+0.5)),uf(:,:,((nx/2)+0.5)),vf(:,:,((nx/2)+0.5)),startx,starty)
% hold off
% title('(x-y plane at z = 0.4) \overrightarrow{\omega} = (1,1,1), $${\sigma = (1,1,1)}$$, $${\alpha = (-1,-1,-1)}$$','Interpreter','Latex','FontSize',16)
% title('OBSEM Eddy (conserves mass)','Interpreter','Latex','FontSize',16)
% xlabel('x','Interpreter','latex','FontSize',16)
% ylabel('y','Interpreter','latex','FontSize',16)
% grid on

toc